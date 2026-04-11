import React, { createContext, useEffect, useState } from 'react';


export const SupabaseContext = createContext();


export function SupabaseAuthProvider({ supabase, children }) {
	const [user, setUser] = useState(null);
	const [initializing, setInitializing] = useState(true);

	useEffect(() => {
		let unsub = null;
		// Supabase v2: getSession returns a promise
			supabase.auth.getSession().then(({ data }) => {
				setUser(data?.session?.user ?? null);
				setInitializing(false);
			});

		// Supabase v2: onAuthStateChange returns a subscription object
		const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
			setUser(session?.user ?? null);
		});

		return () => {
			subscription?.unsubscribe();
		};
	}, [supabase]);

	const value = { supabase, user, initializing };
	return <SupabaseContext.Provider value={value}>{children}</SupabaseContext.Provider>;
}


