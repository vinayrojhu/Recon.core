export interface Permission {
  id: string;
  name: string;
  description: string | null;
}

export interface Role {
  id: string;
  name: string;
  description: string | null;
  permissions: Permission[];
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  roles: Role[];
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
