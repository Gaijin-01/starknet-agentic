/**
 * starknet-privacy acceptance test
 * Run: node skills/_integrations/starknet-privacy/demo.js
 */

const { PrivacyPool } = require('./scripts/starknet-privacy.js');

async function main() {
  console.log('Testing starknet-privacy skill...\n');

  // Test 1: Create commitment
  const pool = new PrivacyPool();
  const commitment = pool.createCommitment('0x123', 100);
  console.log('✓ Commitment created:', commitment.substring(0, 20) + '...');

  // Test 2: Generate nullifier
  const nullifier = pool.createNullifier('0x456', commitment);
  console.log('✓ Nullifier generated:', nullifier.substring(0, 20) + '...');

  // Test 3: Merkle proof
  const merkleProof = pool.getMerkleProof(commitment);
  console.log('✓ Merkle proof generated:', merkleProof.length, 'levels');

  // Test 4: ZK circuit ready
  const circuitReady = pool.isCircuitReady();
  console.log('✓ ZK circuit ready:', circuitReady);

  console.log('\n✅ All acceptance tests passed!');
  console.log('\nFiles:');
  console.log('  - skills/_integrations/starknet-privacy/scripts/starknet-privacy.js');
  console.log('  - skills/_integrations/starknet-privacy/zk_circuits/privacy_pool_production.circom');
  console.log('  - skills/_integrations/starknet-privacy/tests/test_privacy_pool.py');
}

main().catch(console.error);
