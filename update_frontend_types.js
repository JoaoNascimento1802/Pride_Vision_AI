const fs = require('fs');
let code = fs.readFileSync('frontend/src/api/types.ts', 'utf-8');

const targetEnum = 'supply_chain = "supply_chain",';
const replacementEnum = `supply_chain = "supply_chain",
  runtime = "runtime",`;

code = code.replace(targetEnum, replacementEnum);

const targetAchado = 'guideline: string | null';
const replacementAchado = `guideline: string | null
  
  // Runtime / eBPF
  process_name?: string | null
  pid?: number | null
  syscall?: string | null
  container_id?: string | null
  hit_count?: number
  last_seen_at?: string | null`;

code = code.replace(targetAchado, replacementAchado);
fs.writeFileSync('frontend/src/api/types.ts', code, 'utf-8');
