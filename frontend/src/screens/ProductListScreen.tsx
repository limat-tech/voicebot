// VOCERY/frontend/src/screens/ProductListScreen.tsx
import React from 'react';
import { View, Text } from 'react-native';
import type { StackScreenProps } from '@react-navigation/stack'; // Import
import type { RootStackParamList } from '../../App'; // Adjust path

// Define props type
type ProductListScreenProps = StackScreenProps<RootStackParamList, 'ProductList'>;

const ProductListScreen = ({ navigation }: ProductListScreenProps) => { // Add navigation prop and type it
  return (
    <View style={{flex: 1, alignItems: 'center', justifyContent: 'center'}}>
      <Text>Product List Screen</Text>
      {/* Example: <Button title="Go to Login (for testing)" onPress={() => navigation.navigate('Login')} /> */}
    </View>
  );
};

export default ProductListScreen;
