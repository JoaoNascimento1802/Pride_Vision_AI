const fs = require('fs');
let code = fs.readFileSync('backend/tests/test_runtime.py', 'utf-8');

code = code.replace(
    /def test_ac_rt_01_ingest_and_deduplicate\(db: Session\):/,
    'def test_ac_rt_01_ingest_and_deduplicate(db: Session):\n    """AC-RT-01 - Webhook."""'
);

code = code.replace(
    /def test_ac_rt_02_reachability_correlation\(db: Session\):/,
    'def test_ac_rt_02_reachability_correlation(db: Session):\n    """AC-RT-02 - Reachability."""'
);

fs.writeFileSync('backend/tests/test_runtime.py', code, 'utf-8');
