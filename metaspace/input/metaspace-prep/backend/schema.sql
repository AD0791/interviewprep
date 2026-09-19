-- =====================================================================
-- Schema for the on-chain/off-chain integration layer.
--
-- READ THE COMMENTS. Every constraint here exists because of a specific
-- failure mode, and "why is that unique key there?" is a question a Tech
-- Lead can ask in ten seconds and learn everything from.
--
-- Your ONA.io / HANWASH pipeline instincts transfer directly: this is a
-- checkpointed, idempotent ingestion pipeline whose source happens to be a
-- blockchain instead of a form server. The hard parts are the same ones —
-- at-least-once delivery, replays, and a source of truth you do not own.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Indexer checkpoint
-- ---------------------------------------------------------------------
-- One row per (chain, contract) stream. Storing the block HASH and not only
-- the number is what makes reorg detection possible: on the next poll we ask
-- the node for that block again, and if the hash it returns differs, the
-- chain we indexed no longer exists and we must roll back.
CREATE TABLE indexer_checkpoint (
    stream_id          TEXT PRIMARY KEY,           -- e.g. 'polygon:0xabc...:GameItems'
    chain_id           BIGINT      NOT NULL,
    contract_address   TEXT        NOT NULL,
    last_block_number  BIGINT      NOT NULL,
    last_block_hash    TEXT        NOT NULL,
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 2. Raw events
-- ---------------------------------------------------------------------
-- The unique key is (block_hash, log_index), NOT (tx_hash, log_index).
--
-- Why: during a reorg the SAME logical transaction can be re-included in a
-- different block, keeping its tx_hash. Keying on tx_hash would make the
-- re-inclusion collide with the orphaned row and be silently dropped by
-- ON CONFLICT DO NOTHING — you would lose the event. Keying on block_hash
-- lets both rows exist while we mark the orphan as such.
--
-- This gives us idempotency: replaying a block range is a no-op, so the
-- indexer is safe to crash and restart anywhere. That is the whole trick.
CREATE TABLE chain_event (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chain_id       BIGINT      NOT NULL,
    block_number   BIGINT      NOT NULL,
    block_hash     TEXT        NOT NULL,
    block_time     TIMESTAMPTZ NOT NULL,
    tx_hash        TEXT        NOT NULL,
    log_index      INTEGER     NOT NULL,
    address        TEXT        NOT NULL,
    event_name     TEXT        NOT NULL,
    args           JSONB       NOT NULL,
    orphaned       BOOLEAN     NOT NULL DEFAULT FALSE,
    processed_at   TIMESTAMPTZ,
    CONSTRAINT chain_event_unique UNIQUE (block_hash, log_index)
);

CREATE INDEX chain_event_block_idx   ON chain_event (chain_id, block_number) WHERE NOT orphaned;
CREATE INDEX chain_event_pending_idx ON chain_event (processed_at) WHERE processed_at IS NULL AND NOT orphaned;
-- JSONB GIN index so "all events for this player" is not a sequential scan.
CREATE INDEX chain_event_args_idx    ON chain_event USING GIN (args jsonb_path_ops);

-- ---------------------------------------------------------------------
-- 3. Player inventory (the projection the game actually reads)
-- ---------------------------------------------------------------------
-- Derived state. It can always be rebuilt by replaying chain_event from
-- block 0 — which is the property that lets you fix a projection bug without
-- a migration: truncate, replay, done. Treat the chain as the log and this as
-- a materialised view, exactly like a warehouse fact table over raw extracts.
CREATE TABLE player_inventory (
    wallet      TEXT   NOT NULL,
    item_id     NUMERIC(78,0) NOT NULL,     -- uint256 does not fit in BIGINT
    balance     NUMERIC(78,0) NOT NULL DEFAULT 0,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (wallet, item_id),
    CONSTRAINT balance_non_negative CHECK (balance >= 0)
);

-- ---------------------------------------------------------------------
-- 4. Mint vouchers issued by the game server
-- ---------------------------------------------------------------------
-- The nonce is allocated and stored BEFORE the voucher is signed and handed
-- out, so a crash between signing and delivery cannot re-issue the same nonce
-- for a different reward. UNIQUE (wallet, nonce) enforces that at the
-- database level rather than in application logic.
CREATE TABLE mint_voucher (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    wallet        TEXT        NOT NULL,
    item_id       NUMERIC(78,0) NOT NULL,
    amount        NUMERIC(78,0) NOT NULL,
    nonce         BIGINT      NOT NULL,
    deadline      BIGINT      NOT NULL,     -- unix seconds
    signature     TEXT        NOT NULL,
    reason        TEXT        NOT NULL,     -- 'mission:1042', 'daily_login', ...
    redeemed_tx   TEXT,                     -- filled in by the indexer
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT mint_voucher_unique UNIQUE (wallet, nonce)
);

-- Idempotency on the *business* event: one reward per player per reason.
-- Without this, a retried HTTP call from the game client mints the mission
-- reward twice. This is the off-chain half of replay protection — the
-- on-chain nonce check only stops the same voucher being redeemed twice, not
-- two different vouchers being issued for the same mission.
CREATE UNIQUE INDEX mint_voucher_reason_idx ON mint_voucher (wallet, reason);

-- ---------------------------------------------------------------------
-- 5. Outbound transaction queue (the relayer's outbox)
-- ---------------------------------------------------------------------
-- Never fire-and-forget a transaction. Write the intent, then send, then
-- record the hash. If the process dies mid-send you can reconcile on restart
-- by checking the hash on-chain instead of blindly re-sending and
-- double-spending.
CREATE TABLE outbound_tx (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    idempotency_key TEXT        NOT NULL UNIQUE,  -- caller-supplied; the whole point
    chain_id        BIGINT      NOT NULL,
    from_address    TEXT        NOT NULL,
    to_address      TEXT        NOT NULL,
    data            TEXT        NOT NULL,
    value_wei       NUMERIC(78,0) NOT NULL DEFAULT 0,
    nonce           BIGINT,
    tx_hash         TEXT,
    status          TEXT        NOT NULL DEFAULT 'pending',
        -- pending -> submitted -> mined | failed | replaced
    attempts        INTEGER     NOT NULL DEFAULT 0,
    max_fee_wei     NUMERIC(78,0),
    max_priority_wei NUMERIC(78,0),
    last_error      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT outbound_tx_status_chk
        CHECK (status IN ('pending','submitted','mined','failed','replaced'))
);

-- Only one in-flight transaction per (sender, nonce). Two transactions
-- sharing a nonce is exactly the "stuck mempool" incident you get paged for.
CREATE UNIQUE INDEX outbound_tx_nonce_idx
    ON outbound_tx (from_address, nonce)
    WHERE status IN ('submitted','mined');

-- ---------------------------------------------------------------------
-- 6. Auth sessions (SIWE)
-- ---------------------------------------------------------------------
CREATE TABLE auth_nonce (
    nonce       TEXT PRIMARY KEY,
    wallet      TEXT,                        -- bound at issue time if known
    issued_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    consumed_at TIMESTAMPTZ
);
CREATE INDEX auth_nonce_expiry_idx ON auth_nonce (issued_at) WHERE consumed_at IS NULL;
