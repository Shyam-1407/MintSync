# === Imports ===
import discord
from pinata_python.pinning import Pinning
import os
from dotenv import load_dotenv
from transaction import Transaction
import subprocess

# === Global Setup ===
global cid  # declared but not strictly necessary as a global
load_dotenv()  # Load environment variables from .env file

# Set working directory for relative paths (you might want to make this portable in production)
os.chdir(r"C:\Users\Shyam Bhalodiya\OneDrive\Desktop\Lazy-NFT-Minter-Bot-main")

# === Helper Functions ===

def mint_on_sui(metadata_url):
    """
    Calls a Node.js script to mint an NFT on the Sui blockchain.
    """
    try:
        result = subprocess.run(
            ['node', 'transaction_sui.js', metadata_url],
            capture_output=True,
            text=True,
            check=True
        )
        explorer_link = result.stdout.strip()
        return explorer_link
    except subprocess.CalledProcessError as e:
        return f"Error during minting: {e.stderr.strip()}"


def get_mint_number():
    """
    Retrieves the current mint count from a local file.
    """
    if os.path.exists("MINT_COUNTER_FILE.txt"):
        with open("MINT_COUNTER_FILE.txt", 'r') as f:
            return int(f.read().strip())
    return 1


def increment_mint_number():
    """
    Increments and updates the mint counter.
    """
    mint_number = get_mint_number()
    with open("MINT_COUNTER_FILE.txt", 'w') as f:
        f.write(str(mint_number + 1))
    return mint_number

# === Discord Client Setup ===

intents = discord.Intents.default()
intents.message_content = True  # Needed to read message content

client = discord.Client(intents=intents)

# === Pinata Setup ===
pinata = Pinning(
    PINATA_API_KEY=os.getenv("PINATA_API_KEY"),
    PINATA_API_SECRET=os.getenv("PINATA_SECRET_KEY")
)

# === Discord Bot Events ===

@client.event
async def on_ready():
    """
    Event triggered when the bot is ready.
    """
    print(f'✅ Logged in as {client.user}')


@client.event
async def on_message(message):
    """
    Handles incoming messages, checks for image attachments, and processes NFT minting.
    """
    if message.author == client.user:
        return  # Prevent the bot from responding to itself

    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith('image/'):
                try:
                    # === Save image locally ===
                    image_path = f"./images/{attachment.filename}"
                    await attachment.save(image_path)
                    await message.channel.send("✅ Image saved successfully!")

                    # === Pin image to IPFS via Pinata ===
                    response = pinata.pin_file_to_ipfs(image_path)
                    cid = response['IpfsHash']
                    image_cid = f"https://ipfs.io/ipfs/{cid}"

                    # === Create metadata ===
                    new_token = get_mint_number()
                    metadata = {
                        "name": f"#{new_token}",
                        "description": "This is an NFT minted via Discord Bot.",
                        "image": image_cid,
                        "attributes": [
                            {"trait_type": "Minted By", "value": "User"}
                        ]
                    }

                    # === Pin metadata to IPFS ===
                    response_meta = pinata.pin_json_to_ipfs(metadata)
                    meta_cid = response_meta['IpfsHash']
                    metadata_url = f"https://gateway.pinata.cloud/ipfs/{meta_cid}"

                    await message.channel.send("📝 Metadata pinned. Preparing to mint...")
                    await message.channel.send("⏳ Please wait, minting in progress...")

                    # === Mint NFT on Sui Blockchain ===
                    sui_result = mint_on_sui(f"https://gateway.pinata.cloud/ipfs/{cid}")
                    if "Error" not in sui_result:
                        await message.channel.send(f"🎉 NFT minted on Sui!\n {sui_result}")
                    else:
                        await message.channel.send(f"❌ Minting failed:\n{sui_result}")

                    # === Ethereum Transaction (assuming Transaction handles this) ===
                    tx_hash = Transaction(metadata_url)
                    await message.channel.send("🎉 NFT metadata transaction complete!")
                    await message.channel.send(f"📦 Transaction: https://sepolia.etherscan.io/tx/0x{tx_hash}")
                    await message.channel.send(f"🌊 View on OpenSea: https://testnets.opensea.io/assets/sepolia/0x8f1A6030684f975DaDfc2A8c2c52a1D5C783d492/{new_token + 1}")

                    # === Update mint count ===
                    increment_mint_number()

                except Exception as e:
                    await message.channel.send(f"⚠️ Error: {e}")
                break  # Only process the first valid image

# === Start the Bot ===
client.run(os.getenv("BOT_TOKEN"))
