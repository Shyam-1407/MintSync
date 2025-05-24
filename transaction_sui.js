// Load environment variables from .env file
import 'dotenv/config';

// Import required Sui libraries
import { Ed25519Keypair } from '@mysten/sui/keypairs/ed25519';
import { SuiClient } from '@mysten/sui/client';
import { Transaction } from '@mysten/sui/transactions';

// Get the metadata URL passed as a CLI argument
const metadata = process.argv[2];

// Load sensitive config values from environment variables
const privateKeyHex = process.env.SUI_PRIVATE_KEY;    // Your private key (hex string)
const suiUrl = process.env.SUI_RPC_URL;               // Sui fullnode URL (e.g., devnet)
const packageId = process.env.PACKAGE_ID;             // Deployed package ID of your Move contract

// Async function to mint NFT on Sui
async function mintNFT(metadata) {
  if (!metadata) {
    throw new Error("❌ Metadata URL is undefined. Pass it as a CLI argument.");
  }

  // Connect to Sui fullnode
  const client = new SuiClient({ url: suiUrl });

  // Construct keypair from private key
  const keypair = Ed25519Keypair.fromSecretKey(Buffer.from(privateKeyHex, 'hex'));

  // Build a new transaction
  const tx = new Transaction();

  // Call the Move function: `nft_minter::mint_nft` with name, description, and metadata URL
  tx.moveCall({
    target: `${packageId}::nft_minter::mint_nft`,
    arguments: [
      tx.pure('string', 'My NFT'),              // NFT name
      tx.pure('string', 'Made by Bot'),         // NFT description
      tx.pure('string', metadata),              // Metadata URL (from IPFS)
    ],
  });

  // Sign and submit transaction
  const result = await client.signAndExecuteTransaction({
    signer: keypair,
    transaction: tx,
    options: {
      showEffects: true,
      showEvents: true,
    },
  });

  // Extract and display the minted object ID
  const objectId = result.effects?.created?.[0]?.reference?.objectId;
  if (objectId) {
    console.log(`✅ NFT minted: https://devnet.suivision.xyz/object/${objectId}`);
  } else {
    console.error('❌ Failed to extract object ID');
  }
}

// Run the function with error handling
mintNFT(metadata).catch(console.error);

