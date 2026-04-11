import { useContext } from 'react';
import { SupabaseContext } from './supabaseClient';

export function useSupabase() {
  return useContext(SupabaseContext);
}
