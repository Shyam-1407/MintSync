module nft_mint::nft_minter {

    // Importing necessary modules
    use sui::object::{Self, UID};                     // For object creation (UID)
    use sui::tx_context::{Self, TxContext};           // Transaction context (who sent the tx)
    use sui::transfer;                                // For transferring objects
    use std::string::String;                          // Import the String type

    /// NFT struct that holds metadata fields: name, description, and url.
    struct NFT has key, store {
        id: UID,              // Unique object ID
        name: String,         // Name of the NFT
        description: String,  // Description of the NFT
        url: String,          // Metadata URL (typically IPFS link)
    }

    /// Public function to mint an NFT and transfer it to the caller.
    /// - `name`: The name of the NFT
    /// - `description`: A short description
    /// - `url`: Link to metadata or image
    /// - `ctx`: Transaction context
    public entry fun mint_nft(
        name: String,
        description: String,
        url: String,
        ctx: &mut TxContext
    ) {
        // Create a new NFT object
        let nft = NFT {
            id: object::new(ctx),
            name,
            description,
            url,
        };

        // Transfer the NFT to the sender's wallet
        transfer::public_transfer(nft, tx_context::sender(ctx));
    }
}
