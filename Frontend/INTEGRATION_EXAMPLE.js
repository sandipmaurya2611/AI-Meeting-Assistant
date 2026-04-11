// Add this to your App.jsx routes

import JoinMeeting from './Pages/JoinMeeting';

// In your Routes:
<Route path="/join/:roomName" element={<JoinMeeting />} />


// Example: How to integrate InviteParticipants into your existing MeetingInterface.jsx

import InviteParticipants from '../components/InviteParticipants';

// Add these states:
const [showInviteModal, setShowInviteModal] = useState(false);
const [meetingUrl, setMeetingUrl] = useState('');
const [roomName, setRoomName] = useState('');

// When creating/joining meeting, save the meeting URL:
useEffect(() => {
    // After creating or fetching meeting
    const initMeeting = async () => {
        // If creating new meeting:
        const response = await fetch('http://localhost:8000/api/meetings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                host_id: currentUser.id,
                title: 'My Meeting'
            })
        });

        const meeting = await response.json();
        setMeetingUrl(meeting.meeting_url);
        setRoomName(meeting.room_name);

        // Or if joining existing:
        // const meeting = await fetch(`http://localhost:8000/api/meetings/room/${roomFromURL}`);
        // setMeetingUrl(meeting.meeting_url);
    };

    initMeeting();
}, []);

// Add invite button to your UI:
<button
    onClick={() => setShowInviteModal(true)}
    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
>
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
    Invite
</button>

// Add the modal at the end of your component:
{
    showInviteModal && (
        <InviteParticipants
            meetingUrl={meetingUrl}
            roomName={roomName}
            onClose={() => setShowInviteModal(false)}
        />
    )
}
