export interface User {
  id: number;
  email: string;
  full_name: string | null;
  role: "admin" | "trader" | "subscriber";
  is_active: boolean;
  subscription_status: "active" | "trial" | "expired" | "cancelled";
  subscription_expires_at: string | null;
  created_at: string;
}

export interface APIKey {
  id: number;
  user_id: number;
  label: string;
  testnet: boolean;
  leverage: number;
  margin_type: string; // ISOLATED or CROSS
  permissions: { trade: boolean; withdraw: boolean };
  created_at: string;
  api_key?: string | null; // Only for creation
  secret_key?: string | null;
}

export interface Position {
  id: number;
  api_key_id: number;
  symbol: string;
  side: "LONG" | "SHORT";
  entry_price: number;
  mark_price: number;
  quantity: number;
  leverage: number;
  unrealized_pnl: number;
  liquidation_price: number;
  margin: number;
  updated_at: string;
}

export interface Trade {
  id: number;
  user_id: number;
  api_key_id: number;
  symbol: string;
  side: "BUY" | "SELL";
  order_type: string;
  quantity: number;
  price: number;
  fee: number;
  realized_pnl: number;
  order_id: string | null;
  status: string;
  executed_at: string;
}

export interface SubscriptionPlan {
  name: string;
  max_accounts: number;
  max_daily_trades: number;
  features: string[];
  price_monthly: number;
}

export interface Balance {
  asset: string;
  balance: string;
  availableBalance: string;
  crossWalletBalance: string;
  crossUnPnl: string;
}
