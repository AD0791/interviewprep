import fs from "node:fs";
import { createRequire } from "node:module";
const solc = createRequire(import.meta.url)("solc");
const sources = {};
for (const f of fs.readdirSync("src")) sources[f] = { content: fs.readFileSync(`src/${f}`, "utf8") };
const out = JSON.parse(solc.compile(JSON.stringify({
  language: "Solidity", sources,
  settings: { optimizer: { enabled: true, runs: 200 }, outputSelection: { "*": { "*": ["abi", "evm.bytecode.object", "evm.deployedBytecode.object"] } } },
})));
for (const e of out.errors ?? []) console.log(`[${e.severity}] ${e.formattedMessage.split("\n")[0]}`);
const artifacts = {};
for (const [file, cs] of Object.entries(out.contracts ?? {}))
  for (const [name, c] of Object.entries(cs)) {
    artifacts[name] = {
      abi: c.abi,
      bytecode: `0x${c.evm.bytecode.object}`,               // creation code, for deploying
      deployedBytecode: `0x${c.evm.deployedBytecode.object}`, // runtime code, for the size check
    };
    console.log(`OK ${name}: ${c.evm.deployedBytecode.object.length / 2} bytes (EIP-170 limit 24576)`);
  }

// Written so level 10 can prove, mechanically, that the type hash the
// TypeScript signer computes is the same 32 bytes the compiler embedded in the
// contract. Artifacts are build output: regenerate them, do not edit them.
fs.writeFileSync("artifacts.json", JSON.stringify(artifacts, null, 2));
console.log("wrote artifacts.json");
