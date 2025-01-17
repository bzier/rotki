import { z } from 'zod';

export enum HistoryEventType {
  TRADE = 'trade',
  STAKING = 'staking',
  DEPOSIT = 'deposit',
  WITHDRAWAL = 'withdrawal',
  TRANSFER = 'transfer',
  SPEND = 'spend',
  RECEIVE = 'receive',
  ADJUSTMENT = 'adjustment',
  UNKNOWN = 'unknown',
  INFORMATIONAL = 'informational',
  MIGRATE = 'migrate',
  RENEW = 'renew'
}

export const HistoryEventTypeEnum = z.nativeEnum(HistoryEventType);
export type HistoryEventTypeEnum = z.infer<typeof HistoryEventTypeEnum>;

export enum HistoryEventSubType {
  REWARD = 'reward',
  DEPOSIT_ASSET = 'deposit asset',
  REMOVE_ASSET = 'remove asset',
  FEE = 'fee',
  SPEND = 'spend',
  RECEIVE = 'receive',
  APPROVE = 'approve',
  DEPLOY = 'deploy',
  AIRDROP = 'airdrop',
  BRIDGE = 'bridge',
  GOVERNANCE_PROPOSE = 'governance propose',
  GENERATE_DEBT = 'generate debt',
  PAYBACK_DEBT = 'payback debt',
  RECEIVE_WRAPPED = 'receive wrapped',
  RETURN_WRAPPED = 'return wrapped',
  DONATE = 'donate',
  NFT = 'nft',
  PLACE_ORDER = 'place order'
}

export const HistoryEventSubTypeEnum = z.nativeEnum(HistoryEventSubType);
export type HistoryEventSubTypeEnum = z.infer<typeof HistoryEventSubTypeEnum>;

export enum TransactionEventType {
  GAS = 'gas',
  SEND = 'send',
  RECEIVE = 'receive',
  APPROVAL = 'approval',
  DEPOSIT = 'deposit',
  WITHDRAW = 'withdraw',
  AIRDROP = 'airdrop',
  BORROW = 'borrow',
  REPAY = 'repay',
  DEPLOY = 'deploy',
  BRIDGE = 'bridge',
  GOVERNANCE_PROPOSE = 'governance_propose',
  DONATE = 'donate',
  NFT = 'nft'
}

export const TransactionEventTypeEnum = z.nativeEnum(TransactionEventType);
export type TransactionEventTypeEnum = z.infer<typeof TransactionEventTypeEnum>;

export enum TransactionEventProtocol {
  COMPOUND = 'compound',
  GAS = 'gas',
  GITCOIN = 'gitcoin',
  MAKERDAO = 'makerdao',
  UNISWAP = 'uniswap',
  AAVE = 'aave',
  XDAI = 'xdai',
  ZKSYNC = 'zksync',
  '1INCH' = '1inch',
  VOTIUM = 'votium'
}
