export interface User {
  id: number;
  email: string;
  full_name: string;
  is_verified: boolean;
  created_at: string;
  github_login: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
