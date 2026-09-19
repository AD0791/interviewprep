// Minimal solc driver so the contracts can be compiled without Foundry or
// Hardhat installed. `node compile.mjs` prints errors and gas-relevant
// warnings. In a real project use Foundry (`forge build`) — this exists so
// the repo verifies anywhere Node runs.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const solc = require("solc");

const SRC = path.resolve("src");
const sources = {};
for (const file of fs.readdirSync(SRC)) {
  if (file.endsWith(".sol")) {
    sources[`src/${file}`] = { content: fs.readFileSync(path.join(SRC, file), "utf8") };
  }
}

function findImport(importPath) {
  const candidates = [
    path.resolve("node_modules", importPath),
    path.resolve(importPath),
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return { contents: fs.readFileSync(candidate, "utf8") };
    }
  }
  return { error: `not found: ${importPath}` };
}

const input = {
  language: "Solidity",
  sources,
  settings: {
    optimizer: { enabled: true, runs: 200 },
    // viaIR avoids "stack too deep" in the staking math and is what you would
    // ship anyway for a contract with this many locals.
    viaIR: false,
    outputSelection: { "*": { "*": ["abi", "evm.bytecode.object", "evm.gasEstimates"] } },
  },
};

const output = JSON.parse(solc.compile(JSON.stringify(input), { import: findImport }));

let failed = false;
for (const err of output.errors ?? []) {
  if (err.severity === "error") { failed = true; console.error(err.formattedMessage); }
  else if (!/SPDX|Unused|pragma/i.test(err.formattedMessage)) {
    console.warn("warning:", err.formattedMessage.split("\n")[0]);
  }
}

if (!failed) {
  fs.mkdirSync("out", { recursive: true });
  for (const [file, contracts] of Object.entries(output.contracts ?? {})) {
    for (const [name, artifact] of Object.entries(contracts)) {
      const bytes = (artifact.evm?.bytecode?.object?.length ?? 0) / 2;
      // EIP-170 caps deployed contract size at 24,576 bytes. Blowing past it
      // is a deploy-time failure that surprises people late; check early.
      console.log(`OK  ${file}:${name}  ${bytes} bytes${bytes > 24576 ? "  <-- EXCEEDS EIP-170" : ""}`);
      fs.writeFileSync(path.join("out", `${name}.json`), JSON.stringify({ abi: artifact.abi }, null, 2));
    }
  }
}

process.exit(failed ? 1 : 0);
