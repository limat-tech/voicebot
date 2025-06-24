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
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App';

const audioRecorderPlayer = new AudioRecorderPlayer();

type Product = {
    product_id: number;
    name_en: string;
    name_ar: string;
    description_en?: string;
    description_ar?: string;
    price: number;
    brand?: string;
    stock_quantity: number;
    unit_type: string;
    image_url?: string;
    category_id: number;
    is_active: boolean;
};

type VoiceResponsePayload = {
  nlu_result: {
    intent: { name: string };
    entities: { entity: string; value: string }[];
    transcript: string;
  };
  response_text: string;
  audio_filename: string | null;
  order_id: number | null;
};

type ProductListScreenProps = StackScreenProps<RootStackParamList, 'ProductList'>;

const ProductListScreen = ({ navigation }: ProductListScreenProps) => {
    const [products, setProducts] = useState<Product[]>([]);
    const [originalProducts, setOriginalProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [searchTerm, setSearchTerm] = useState<string>('');
    const [isRecording, setIsRecording] = useState(false);
    // Re-instating two separate states for a better UI
    const [statusMessage, setStatusMessage] = useState('Tap microphone to speak');
    const [transcriptMessage, setTranscriptMessage] = useState('');

    // Robust audio playback with defensive listener
    const playAudioFromUrl = async (url: string) => {
        setStatusMessage('Playing response...');
        try {
            await audioRecorderPlayer.startPlayer(url);
            audioRecorderPlayer.addPlayBackListener((e) => {
                if (e.duration > 0 && e.currentPosition >= e.duration) {
                    audioRecorderPlayer.stopPlayer();
                    audioRecorderPlayer.removePlayBackListener();
                    setStatusMessage('Tap microphone to speak');
                }
            });
        } catch (error) {
            console.error('Failed to play audio from URL:', error);
            setStatusMessage('Error: Could not play response');
        }
    };
    
    // Recording logic
    const startRecording = async () => {
        const hasPermission = await requestPermissions();
        if (!hasPermission) {
            Alert.alert('Permission Required', 'Microphone permission is needed.');
            return;
        }
        setTranscriptMessage(''); 
        setIsRecording(true);
        setStatusMessage('Recording...');
        try {
            await audioRecorderPlayer.startRecorder();
            audioRecorderPlayer.addRecordBackListener((e) => {
                setStatusMessage(`Recording... ${e.currentPosition.toFixed(1)}s`);
            });
        } catch (e) {
            console.error('Failed to start recording', e);
            setIsRecording(false);
        }
    };

    const stopRecording = async () => {
        setIsRecording(false);
        setStatusMessage('Processing...');
        try {
            const resultPath = await audioRecorderPlayer.stopRecorder();
            audioRecorderPlayer.removeRecordBackListener();
            handleVoiceUpload(resultPath);
        } catch (e) {
            console.error('Failed to stop recording', e);
        }
    };

    // API Communication with fixes for UI and audio playback
    const handleVoiceUpload = async (filePath: string) => {
        const formData = new FormData();
        formData.append('audio', {
            uri: Platform.OS === 'android' ? `file://${filePath}` : filePath,
            type: 'audio/wav',
            name: 'voice_command.wav',
        });

        const API_BASE_URL = 'http://10.0.2.2:5000/api/voice';

        try {
            const token = await AsyncStorage.getItem('userToken');
            if (!token) {
                setStatusMessage('Error: You are not logged in.');
                navigation.replace('Login');
                return;
            }

            const response = await axios.post<VoiceResponsePayload>(`${API_BASE_URL}/process`, formData, {
                headers: { 
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${token}`
                },
                timeout: 30000, 
            });
            
            const { nlu_result, audio_filename,order_id } = response.data;
            
            // Set the persistent transcript message
            if (nlu_result && nlu_result.transcript) {
                setTranscriptMessage(`Heard: "${nlu_result.transcript}"`);
            } else {
                setTranscriptMessage("Sorry, I couldn't understand that.");
            }
            // Clear the status message, as the transcript now provides the primary feedback
            setStatusMessage('');

            const intent = nlu_result?.intent?.name;
            const productEntity = nlu_result?.entities?.find(e => e.entity === 'product_name');

            if (intent === 'search_product' && productEntity) {
                setSearchTerm(productEntity.value);
            } else if (intent === 'view_cart') {
                navigation.navigate('Cart');
            } else if (intent === 'go_to_checkout' && order_id) {
                navigation.navigate('OrderDetail',{orderId: order_id});
            }

            if (audio_filename) {
                const audioUrl = `${API_BASE_URL}/audio/${audio_filename}`;
                // Use a timeout to prevent re-renders from interrupting the player
                setTimeout(() => playAudioFromUrl(audioUrl), 100);
            } else {
                setTimeout(() => setStatusMessage('Tap microphone to speak'), 4000);
            }

        } catch (error) {
            console.error('Error during voice processing:', error);
            setTranscriptMessage(''); // Clear transcript on error
            if (axios.isAxiosError(error) && error.response?.status === 401) {
                setStatusMessage('Session expired. Please log in again.');
                navigation.replace('Login');
            } else {
                setStatusMessage('Error: Could not process request.');
            }
        }
    };
    
    // --- Unchanged Code Below ---
    const requestPermissions = async () => {
        if (Platform.OS === 'android') {
            try {
                const granted = await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.RECORD_AUDIO);
                return granted === PermissionsAndroid.RESULTS.GRANTED;
            } catch (err) {
                console.warn(err);
                return false;
            }
        }
        return true;
    };

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

    useEffect(() => {
        const loadInitialData = async () => {
            setLoading(true);
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) { navigation.replace('Login'); return; }
                const response = await axios.get('http://10.0.2.2:5000/api/products', { headers: { Authorization: `Bearer ${token}` } });
                const fetchedProducts = response.data.products || response.data;
                console.log('Raw API response:', JSON.stringify(response.data, null, 2));
                console.log('Fetched products:', JSON.stringify(fetchedProducts.slice(0, 2), null, 2)); // Log first 2 products
                if (Array.isArray(fetchedProducts)) {
                    setProducts(fetchedProducts);
                    setOriginalProducts(fetchedProducts);
                }
            } catch (error) { console.error('Failed to fetch initial products:', error); }
            finally { setLoading(false); }
        };
        loadInitialData();
        return () => {
            audioRecorderPlayer.removeRecordBackListener();
            audioRecorderPlayer.removePlayBackListener();
        };
    }, [navigation]);

    useEffect(() => {
        if (searchTerm.trim() === '') { setProducts(originalProducts); return; }
        const handleSearch = async () => {
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) { return; }
                const response = await axios.get(`http://10.0.2.2:5000/api/products/search?q=${encodeURIComponent(searchTerm)}`, { headers: { Authorization: `Bearer ${token}` } });
                setProducts(response.data.products || response.data);
            } catch (error) { console.error("Search failed:", error); setProducts([]); }
        };
        const delayDebounceFn = setTimeout(() => { handleSearch(); }, 300);
        return () => clearTimeout(delayDebounceFn);
    }, [searchTerm, originalProducts]);

    const renderItem = ({ item }: { item: Product }) => (
    <TouchableOpacity 
        style={styles.itemContainer} 
        onPress={() => navigation.navigate('ProductDetail', { productId: item.product_id })}
    >
        {/* English name as main title */}
        <Text style={styles.itemNamePrimary}>
            {item.name_en || 'Product Name'}
        </Text>
        
        {/* Arabic name as subtitle */}
        {item.name_ar && (
            <Text style={styles.itemNameSecondary}>
                {item.name_ar}
            </Text>
        )}
        
        <Text style={styles.itemPrice}>
            Price: ${item.price ? item.price.toFixed(2) : 'N/A'}
        </Text>
        
        {/* Optional: Show brand if available */}
        {item.brand && (
            <Text style={styles.itemBrand}>
                Brand: {item.brand}
            </Text>
        )}
    </TouchableOpacity>
);
    return (
        <View style={styles.container}>
            <TextInput style={styles.searchInput} placeholder="Search or use voice..." value={searchTerm} onChangeText={setSearchTerm} clearButtonMode="while-editing" />
            {loading ? (
                <ActivityIndicator size="large" color="#0000ff" style={{ marginTop: 20 }} />
            ) : (
                <FlatList data={products} renderItem={renderItem} keyExtractor={(item) => item.product_id.toString()} contentContainerStyle={styles.listContainer} ListEmptyComponent={<Text style={styles.emptyText}>No products found.</Text>} />
            )}
            <View style={styles.voiceContainer}>
                <TouchableOpacity onPress={isRecording ? stopRecording : startRecording} style={[styles.micButton, isRecording && styles.micButtonActive]}>
                    <Text style={styles.micButtonText}>{isRecording ? 'STOP' : 'MIC'}</Text>
                </TouchableOpacity>
                <Text style={styles.voiceStatusText}>{statusMessage}</Text>
                {transcriptMessage ? (
                    <Text style={styles.transcriptText}>{transcriptMessage}</Text>
                ) : null}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f8f8f8' },
    headerRightContainer: { flexDirection: 'row', marginRight: 10 },
    headerButton: { marginLeft: 15 },
    headerButtonText: { fontSize: 16 },
    searchInput: { height: 45, borderColor: '#ddd', borderWidth: 1, borderRadius: 8, paddingHorizontal: 15, margin: 10, backgroundColor: '#fff', fontSize: 16 },
    listContainer: { paddingHorizontal: 10, paddingBottom: 160 },
    itemContainer: { backgroundColor: '#fff', padding: 15, marginVertical: 8, borderRadius: 8, elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.2, shadowRadius: 1.41 },
    itemName: { fontSize: 18, fontWeight: 'bold', color: '#333' },
    itemPrice: { fontSize: 16, color: 'green', marginTop: 5 },
    emptyText: { fontSize: 18, color: '#888', textAlign: 'center', marginTop: 50 },
    voiceContainer: { position: 'absolute', bottom: 0, left: 0, right: 0, padding: 20, backgroundColor: 'rgba(255, 255, 255, 0.95)', borderTopWidth: 1, borderTopColor: '#e0e0e0', alignItems: 'center' },
    micButton: { width: 70, height: 70, borderRadius: 35, backgroundColor: '#007AFF', justifyContent: 'center', alignItems: 'center', marginBottom: 10, elevation: 5 },
    micButtonActive: { backgroundColor: '#FF3B30' },
    micButtonText: { fontSize: 16, fontWeight: 'bold', color: 'white' },
    voiceStatusText: { 
        minHeight: 20,
        fontSize: 14,
        color: '#666',
        textAlign: 'center',
        fontStyle: 'italic',
    },
    transcriptText: {
        marginTop: 5,
        fontSize: 16,
        color: '#000',
        textAlign: 'center',
        fontWeight: '500',
        paddingHorizontal: 10,
    },
    itemNamePrimary: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 2,
    },
    itemNameSecondary: {
        fontSize: 16,
        fontWeight: '500',
        color: '#222',
        fontStyle: 'italic',
        marginBottom: 2,
        textAlign: 'right', // Right-align Arabic text
    },
    itemBrand: {
        fontSize: 12,
        color: '#888',
        fontStyle: 'italic',
    },
});

export default ProductListScreen;
