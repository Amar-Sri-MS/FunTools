// Registering click event handler to track web events
document.addEventListener('click', function(element) {
    // Only track elements with the data attribute "web_event"
    if (element.target.dataset['web_event']) {
        trackWebEvent(element.target.dataset['web_event']);
    }
});

function trackWebEvent(eventName, data=null) {
    // Create an event object with event name and
    // timestamp
    const eventData = {
        event: eventName,
        data,
        timestamp: Date.now(),
        logID: typeof logId !== "undefined" ? logId : null
    }

    const TRACK_WEB_EVENT_API = `${window.location.origin}/events/track`;
    fetchWrapper.post(TRACK_WEB_EVENT_API, eventData);
}