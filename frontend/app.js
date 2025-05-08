document.getElementById('subscribeBtn').addEventListener('click', () => {
  const userId = document.getElementById('userIdInput').value.trim();
  if (!userId) {
    alert('Please enter a User ID');
    return;
  }
  fetch('/subscribe', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user_id: userId})
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('subscriptionMessage').textContent = data.message || data.error;
  })
  .catch(err => {
    document.getElementById('subscriptionMessage').textContent = 'Error subscribing user.';
  });
});

document.getElementById('unsubscribeBtn').addEventListener('click', () => {
  const userId = document.getElementById('userIdInput').value.trim();
  if (!userId) {
    alert('Please enter a User ID');
    return;
  }
  fetch('/unsubscribe', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user_id: userId})
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('subscriptionMessage').textContent = data.message || data.error;
  })
  .catch(err => {
    document.getElementById('subscriptionMessage').textContent = 'Error unsubscribing user.';
  });
});

document.getElementById('analyzeBtn').addEventListener('click', () => {
  const userId = document.getElementById('userIdInput').value.trim();
  const legalText = document.getElementById('legalTextInput').value.trim();
  if (!userId || !legalText) {
    alert('Please enter both User ID and legal text');
    return;
  }
  fetch('/legal-analytics', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user_id: userId, legal_text: legalText})
  })
  .then(res => res.json())
  .then(data => {
    if (data.insights) {
      document.getElementById('analysisResult').textContent = JSON.stringify(data.insights, null, 2);
    } else {
      document.getElementById('analysisResult').textContent = data.error || 'No insights returned.';
    }
  })
  .catch(err => {
    document.getElementById('analysisResult').textContent = 'Error analyzing legal text.';
  });
});

document.getElementById('sendFeedbackBtn').addEventListener('click', () => {
  const feedback = document.getElementById('feedbackInput').value.trim();
  if (!feedback) {
    alert('Please enter feedback');
    return;
  }
  fetch('/feedback', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({feedback})
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('feedbackMessage').textContent = data.message || 'Feedback sent.';
    document.getElementById('feedbackInput').value = '';
  })
  .catch(err => {
    document.getElementById('feedbackMessage').textContent = 'Error sending feedback.';
  });
});
