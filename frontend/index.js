

import { AppRegistry } from 'react-native';
import React from 'react';
import App from './App'; // This is your main App.tsx file
import { name as appName } from './app.json';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

// Create a new component that wraps your App with the GestureHandlerRootView
const AppWithGestureHandler = () => (
  <GestureHandlerRootView style={{ flex: 1 }}>
    <App />
  </GestureHandlerRootView>
);

// Register the new wrapped component as the main entry point
AppRegistry.registerComponent(appName, () => AppWithGestureHandler);
