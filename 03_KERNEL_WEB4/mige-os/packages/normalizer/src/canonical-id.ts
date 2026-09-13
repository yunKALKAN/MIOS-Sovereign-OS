export enum Blockchain {
  ETHEREUM = 'ethereum',
  SOLANA = 'solana',
  BNB_CHAIN = 'bnb_chain',
  POLYGON = 'polygon',
  ARBITRUM = 'arbitrum',
  OPTIMISM = 'optimism',
  AVALANCHE = 'avalanche',
  BASE = 'base',
  UNKNOWN = 'unknown'
}

export interface CanonicalID {
  readonly blockchain: Blockchain;
  readonly address: string;
  readonly network: string;
}