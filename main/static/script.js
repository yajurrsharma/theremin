let currentSequence = [];
let isRecording = false;


const instrumentMap = {
    1: 'kick',
    2: 'snare',
    3: 'hi-hat',
    4: 'bass',
    5: 'synth'
};

function toggleInstrument(id) {
    const index = currentSequence.indexOf(id);
    if (index > -1) {
        currentSequence.splice(index, 1);
    } else {
        currentSequence.push(id);
    }

    updateUI();
    sendSequence();
}

function updateUI() {
    for (let i = 1; i <= 5; i++) {
        const btn = document.getElementById(`btn-${i}`);
        const badge = btn.querySelector('.order-badge');
        btn.style.borderColor = '#52525b';
        btn.style.backgroundColor = '#000000';
        badge.innerText = '';
    }

    currentSequence.forEach((id, idx) => {
        const btn = document.getElementById(`btn-${id}`);
        const badge = btn.querySelector('.order-badge');
        btn.style.borderColor = '#ffffff';
        btn.style.backgroundColor = '#09090b';
        badge.innerText = `${idx + 1}`;
        badge.style.color = '#ffffff';
    });
}

function sendSequence() {
    const seqToSend = currentSequence.map(id => instrumentMap[id]);

    fetch('/api/set_sequence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequence: seqToSend })
    })
    .then(res => res.json())
    .catch(err => console.error('Error updating sequence:', err));
}

function toggleRecord() {
    isRecording = !isRecording;
    const btn = document.getElementById('recordBtn');
    if (isRecording) {
        btn.style.borderColor = '#ef4444';
        btn.style.color = '#ef4444';
        btn.innerText = 'RECORDING.';
        fetch('/api/start_recording', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
            .catch(err => console.error('Error starting record:', err));
    } else {
        btn.style.borderColor = '#ffffff';
        btn.style.color = '#e4e4e7';
        btn.innerText = 'RECORD';
        fetch('/api/stop_track', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
            .catch(err => console.error('Error stopping track:', err));
    }
}

function finalizeAndPlay() {
    fetch('/finalize_and_play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        console.log('Loop playback status:', data);
    })
    .catch(err => console.error('Error finalizing playback:', err));
}