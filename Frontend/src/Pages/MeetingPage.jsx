import { useAuth } from '../hooks/useAuth';
import MeetingInterface from './MeetingInterface';

export default function MeetingPage() {
    const { user, logout } = useAuth();

    return (
        <MeetingInterface
            user={user}
            signOut={logout}
        />
    );
}