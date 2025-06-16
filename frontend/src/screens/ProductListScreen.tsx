// VOCERY/frontend/src/screens/ProductListScreen.tsx
import React, { useState, useEffect, useLayoutEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    StyleSheet,
    ActivityIndicator,
    TouchableOpacity,
    Alert,
    TextInput,
    Platform,
    PermissionsAndroid
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Voice imports
import Voice, { SpeechResultsEvent, SpeechErrorEvent } from '@react-native-voice/voice';

import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App';

// Product type definition
type Product = {
    product_id: number;
    name_en: string;
    name_ar?: string;
    price: number;
    brand?: string;
    category_id?: number;
    description_ar?: string;
    description_en?: string;
    image_url?: string;
    stock_quantity?: number;
    unit_type?: string;
};

type ProductListScreenProps = StackScreenProps<RootStackParamList, 'ProductList'>;

const ProductListScreen = ({ navigation }: ProductListScreenProps) => {
    // Existing state
    const [products, setProducts] = useState<Product[]>([]);
    const [originalProducts, setOriginalProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [searchTerm, setSearchTerm] = useState<string>('');

    // Voice state management
    const [isListening, setIsListening] = useState(false);
    const [recognizedText, setRecognizedText] = useState('');
    const [voiceError, setVoiceError] = useState('');
    const [voiceAvailable, setVoiceAvailable] = useState(false);
    const [serverResponse, setServerResponse] = useState('');

    // Permission request function
    const requestMicrophonePermission = async () => {
        if (Platform.OS === 'android') {
            try {
                const granted = await PermissionsAndroid.request(
                    PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
                    {
                        title: 'Microphone Permission',
                        message: 'This app needs access to your microphone for voice search.',
                        buttonPositive: 'OK',
                    }
                );
                return granted === PermissionsAndroid.RESULTS.GRANTED;
            } catch (err) {
                console.warn('Permission request error:', err);
                return false;
            }
        }
        return true; // iOS or other platforms
    };

    // Enhanced start/stop listening functions
    const startListening = async () => {
        if (!voiceAvailable) {
            Alert.alert('Voice Not Available', 'Voice recognition is not available on this device.');
            return;
        }

        // Prevent starting if already listening
        if (isListening) {
            console.log('Already listening, ignoring start request');
            return;
        }

        const hasPermission = await requestMicrophonePermission();
        if (!hasPermission) {
            Alert.alert('Permission Required', 'Microphone permission is required for voice search.');
            return;
        }

        try {
            // Ensure clean state before starting
            await Voice.stop();
            
            setRecognizedText('');
            setVoiceError('');
            
            // Wait a brief moment before starting
            setTimeout(async () => {
                try {
                    await Voice.start('en-US');
                } catch (startError) {
                    console.error('Error starting voice after cleanup:', startError);
                    setVoiceError('Failed to start voice recognition');
                    setIsListening(false);
                }
            }, 500);
            
        } catch (error) {
            console.error('Error starting voice:', error);
            setVoiceError('Failed to start voice recognition');
            setIsListening(false);
        }
    };

    const stopListening = async () => {
        try {
            await Voice.stop();
            await Voice.cancel(); // Also cancel any pending recognition
        } catch (error) {
            console.error('Error stopping voice:', error);
            // Force cleanup even if stop fails
            try {
                await Voice.destroy();
            } catch (destroyError) {
                console.error('Error destroying voice after stop failure:', destroyError);
            }
        }
        setIsListening(false);
    };

    // Navigation header setup
    useLayoutEffect(() => {
        navigation.setOptions({
            headerRight: () => (
                <View style={styles.headerRightContainer}>
                    <TouchableOpacity onPress={() => navigation.navigate('Cart')} style={styles.headerButton}>
                        <Text style={styles.headerButtonText}>Cart</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => navigation.navigate('Profile')} style={styles.headerButton}>
                        <Text style={styles.headerButtonText}>Profile</Text>
                    </TouchableOpacity>
                </View>
            ),
        });
    }, [navigation]);

    // Voice availability check
    useEffect(() => {
        const checkVoiceAvailability = async () => {
            try {
                const available = await Voice.isAvailable();
                setVoiceAvailable(!!available);
                if (!available) {
                    setVoiceError('Voice recognition not available on this device');
                }
                console.log('Voice availability:', !!available);
            } catch (error) {
                console.error('Voice availability check failed:', error);
                setVoiceError('Failed to initialize voice services');
                setVoiceAvailable(false);
            }
        };

        checkVoiceAvailability();
    }, []);

    // Enhanced voice event listeners with robust error handling
    useEffect(() => {
        // Voice event handlers
        const onSpeechStart = (e: any) => {
            console.log('Voice started:', e);
            setIsListening(true);
            setVoiceError('');
        };

        const onSpeechEnd = (e: any) => {
            console.log('Voice ended:', e);
            setIsListening(false);
        };

        const onSpeechError = async (e: SpeechErrorEvent) => {
        console.error('Voice error:', e);
        
        // Handle the specific "RecognitionService busy" error (Code 8)
        if (e.error?.code === '8' || e.error?.message?.includes('RecognitionService busy')) {
            console.log('Recognition service is busy, attempting cleanup and retry...');
            
            try {
                await Voice.destroy();
                
                setTimeout(async () => {
                    try {
                        await Voice.removeAllListeners();
                        setIsListening(false);
                        setVoiceError('Voice service reset. Please try again.');
                        
                        // Re-setup the listeners
                        Voice.onSpeechStart = onSpeechStart;
                        Voice.onSpeechEnd = onSpeechEnd;
                        Voice.onSpeechError = onSpeechError;
                        Voice.onSpeechResults = onSpeechResults;
                        
                    } catch (reinitError) {
                        console.error('Failed to reinitialize voice service:', reinitError);
                        setVoiceError('Voice service failed to reset. Please restart the app.');
                    }
                }, 1000);
                
            } catch (destroyError) {
                console.error('Failed to destroy voice service:', destroyError);
                setVoiceError('Please restart the app to reset voice service.');
            }
        } 
        // Handle "Client side error" (Code 5) - NON-CRITICAL
        else if (e.error?.code === '5' || e.error?.message?.includes('Client side error')) {
            console.log('Client side error detected - this is usually non-critical');
            
            // Since voice recognition still works, just log the error and continue
            // Don't show error to user since functionality is not impacted
            setIsListening(false);
            
            // Clear any previous error messages since this is recoverable
            setTimeout(() => {
                setVoiceError('');
            }, 2000); // Clear after 2 seconds
        } 
        // Handle all other speech errors
        else {
            setVoiceError(e.error?.message || 'Speech recognition error');
            setIsListening(false);
        }
    };

        const onSpeechResults = async (e: SpeechResultsEvent) => {
            console.log('Voice results:', e);
            if (e.value && e.value.length > 0) {
                const spokenText = e.value[0];
                setRecognizedText(spokenText);
                setSearchTerm(spokenText); // Connect to existing search functionality

                try {
                    console.log(`Sending transcript to backend: "${spokenText}"`);
                    const response = await axios.post('http://10.0.2.2:5000/api/voice/process', {
                        transcript: spokenText
                    });
                    
                    if (response.data && response.data.responseText) {
                        console.log('Backend response:', response.data.responseText);
                        setServerResponse(response.data.responseText);
                    }
                } catch (error) {
                    console.error('Error calling voice processing API:', error);
                    setServerResponse('Could not connect to the server.');
                }
            }
        };

        // Set up voice listeners
        Voice.onSpeechStart = onSpeechStart;
        Voice.onSpeechEnd = onSpeechEnd;
        Voice.onSpeechError = onSpeechError;
        Voice.onSpeechResults = onSpeechResults;

        return () => {
            // More thorough cleanup
            const cleanup = async () => {
                try {
                    await Voice.stop();
                    await Voice.cancel();
                    await Voice.destroy();
                    Voice.removeAllListeners();
                } catch (error) {
                    console.error('Error during voice cleanup:', error);
                }
            };
            
            cleanup();
        };
    }, []);

    // Initial data loading effect
    useEffect(() => {
        const loadInitialData = async () => {
            setLoading(true);
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) {
                    navigation.replace('Login');
                    return;
                }
                const response = await axios.get('http://10.0.2.2:5000/api/products', {
                    headers: { Authorization: `Bearer ${token}` },
                });
                const fetchedProducts = response.data.products || response.data;
                if (Array.isArray(fetchedProducts)) {
                    setProducts(fetchedProducts);
                    setOriginalProducts(fetchedProducts);
                }
            } catch (error) {
                console.error('Failed to fetch initial products:', error);
            } finally {
                setLoading(false);
            }
        };
        loadInitialData();
    }, []);

    // Search handling effect
    useEffect(() => {
        if (searchTerm.trim() === '') {
            setProducts(originalProducts);
            return;
        }
        const handleSearch = async () => {
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) { return; }
                const response = await axios.get(`http://10.0.2.2:5000/api/products/search?q=${encodeURIComponent(searchTerm)}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setProducts(response.data.products || response.data);
            } catch (error) {
                console.error("Search failed:", error);
                setProducts([]);
            }
        };
        const delayDebounceFn = setTimeout(() => {
            handleSearch();
        }, 300);
        return () => clearTimeout(delayDebounceFn);
    }, [searchTerm, originalProducts]);

    const renderItem = ({ item }: { item: Product }) => (
        <TouchableOpacity
            style={styles.itemContainer}
            onPress={() => navigation.navigate('ProductDetail', { productId: item.product_id })}
        >
            <Text style={styles.itemName}>{item.name_en}</Text>
            <Text style={styles.itemPrice}>Price: ${item.price ? item.price.toFixed(2) : 'N/A'}</Text>
        </TouchableOpacity>
    );

    return (
        <View style={styles.container}>
            <TextInput
                style={styles.searchInput}
                placeholder="Search for products or use voice..."
                value={searchTerm}
                onChangeText={setSearchTerm}
                clearButtonMode="while-editing"
            />
            {loading ? (
                <ActivityIndicator size="large" color="#0000ff" style={{ marginTop: 20 }} />
            ) : (
                <FlatList
                    data={products}
                    renderItem={renderItem}
                    keyExtractor={(item) => item.product_id.toString()}
                    contentContainerStyle={styles.listContainer}
                    ListEmptyComponent={
                        <View style={styles.emptyContainer}>
                            <Text style={styles.emptyText}>No products found.</Text>
                        </View>
                    }
                />
            )}
            
            {/* Voice UI Container */}
            <View style={styles.voiceContainer}>
                <TouchableOpacity 
                    onPress={isListening ? stopListening : startListening} 
                    style={[styles.micButton, isListening && styles.micButtonActive]}
                    disabled={!voiceAvailable}
                >
                    <Text style={styles.micButtonText}>
                        {isListening ? 'STOP' : 'MIC'}
                    </Text>
                </TouchableOpacity>
                
                <Text style={styles.voiceStatusText}>
                    {serverResponse ? serverResponse :
                     isListening ? 'Listening...' : 
                     voiceError ? `Error: ${voiceError}` : 
                     recognizedText ? `"${recognizedText}"` : 
                     voiceAvailable ? 'Tap microphone to speak' : 'Voice not available'}
                </Text>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f8f8',
    },
    headerRightContainer: {
        flexDirection: 'row',
        marginRight: 10,
    },
    headerButton: {
        marginLeft: 15,
    },
    headerButtonText: {
        color: '#fff',
        fontSize: 16,
    },
    searchInput: {
        height: 45,
        borderColor: '#ddd',
        borderWidth: 1,
        borderRadius: 8,
        paddingHorizontal: 15,
        margin: 10,
        backgroundColor: '#fff',
        fontSize: 16,
    },
    listContainer: {
        paddingHorizontal: 10,
        paddingBottom: 150, // Make room for voice UI
    },
    itemContainer: {
        backgroundColor: '#fff',
        padding: 15,
        marginVertical: 8,
        borderRadius: 8,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.2,
        shadowRadius: 1.41,
    },
    itemName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    itemPrice: {
        fontSize: 16,
        color: 'green',
        marginTop: 5,
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 50,
    },
    emptyText: {
        fontSize: 18,
        color: '#888',
    },
    // Voice UI Styles
    voiceContainer: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        padding: 20,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
        alignItems: 'center',
    },
    micButton: {
        width: 70,
        height: 70,
        borderRadius: 35,
        backgroundColor: '#007AFF',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 10,
        elevation: 5,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
    },
    micButtonActive: {
        backgroundColor: '#FF3B30',
    },
    micButtonText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: 'white',
    },
    voiceStatusText: {
        fontSize: 14,
        color: '#666',
        textAlign: 'center',
        fontStyle: 'italic',
    },
});

export default ProductListScreen;