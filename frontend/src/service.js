// service.js
import TrackPlayer from 'react-native-track-player';

module.exports = async function() {
  // This service needs to be registered for the module to work.
  // It runs in a separate process/thread in the background.
  // Event listeners added here will be active even if your main UI component is not.
  TrackPlayer.addEventListener('remote-play', () => TrackPlayer.play());
  TrackPlayer.addEventListener('remote-pause', () => TrackPlayer.pause());
  TrackPlayer.addEventListener('remote-stop', () => TrackPlayer.destroy());
  
  // These are optional, but good for debugging and understanding player state
  TrackPlayer.addEventListener(TrackPlayer.Event.PlaybackTrackChanged, async (data) => {
    console.log(`[TrackPlayer Service] Track changed: ${data.track}`);
  });
  TrackPlayer.addEventListener(TrackPlayer.Event.PlaybackQueueEnded, async (data) => {
    console.log(`[TrackPlayer Service] Queue ended: ${data.track}`);
  });
  TrackPlayer.addEventListener(TrackPlayer.Event.PlaybackError, (data) => {
    console.error(`[TrackPlayer Service] Playback error: ${data.message}`, data);
  });

  // You can add more event listeners here for background controls (next, previous, seek) if you plan to implement them
};
