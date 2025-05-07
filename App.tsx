import React, {useState} from 'react';
import {Button, SafeAreaView, Text, View, Alert, ActivityIndicator} from 'react-native';
import DocumentPicker from 'react-native-document-picker';
import axios from 'axios';
import Video from 'react-native-video';
import RNFS from 'react-native-fs';
import {PermissionsAndroid, Platform} from 'react-native';

const App = () => {
  const [resultUri, setResultUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const uploadFile = async () => {
    try {
      const res = await DocumentPicker.pickSingle({
        type: [DocumentPicker.types.video],
      });

      const data = new FormData();
      data.append('file', {
        uri: res.uri,
        type: res.type,
        name: res.name,
      });

      setLoading(true);
      const response = await axios.post('http://localhost:5001/upload', data, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Save the video to local storage
      const reader = new FileReader();
      reader.onload = async () => {
        const base64data = reader.result?.toString().split(',')[1];
        const path = `${RNFS.DocumentDirectoryPath}/processed_video.mp4`;

        if (base64data) {
          await RNFS.writeFile(path, base64data, 'base64');
          setResultUri(`file://${path}`);
        }

        setLoading(false);
      };
      reader.readAsDataURL(response.data);
    } catch (err) {
      console.error(err);
      Alert.alert('Error', 'Failed to process video');
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
      <Text style={{fontSize: 20, marginBottom: 20}}>Upload MP4 to Detect & Blur Watermark</Text>
      <Button title="Upload Video" onPress={uploadFile} />
      {loading && <ActivityIndicator size="large" style={{marginTop: 20}} />}
      {resultUri && (
        <Video
          source={{uri: resultUri}}
          style={{width: 300, height: 200, marginTop: 20}}
          controls
          resizeMode="contain"
        />
      )}
    </SafeAreaView>
  );
};

export default App;
