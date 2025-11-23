import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Flex,
  Heading,
  Text,
  VStack,
  HStack,
  Avatar,
  useColorModeValue,
  keyframes,
  Badge,
  Icon,
  Divider,
  Code
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useRecorder } from '../hooks/useRecorder';
import { fetchWithAuth } from '../utils/fetchWithAuth';
import Editor from '@monaco-editor/react';
import RecruiterAvatar from '../components/RecruiterAvatar';
import { FaMicrophone, FaMicrophoneSlash, FaPlay, FaCode } from 'react-icons/fa';

const blink = keyframes`
  0% { opacity: 0.2; }
  100% { opacity: 1; }
`;

const DotTypingAnimation = () => (
  <HStack spacing={1} mt={2}>
    {[0, 0.2, 0.4].map((delay, i) => (
      <Box
        key={i}
        w="6px"
        h="6px"
        bg="gray.400"
        borderRadius="full"
        animation={`${blink} 1s ${delay}s infinite alternate`}
      />
    ))}
  </HStack>
);

export default function CodingPage() {
  // --- LOGIC START (UNCHANGED) ---
  const [problem, setProblem] = useState<any>(null);
  const [code, setCode] = useState('');
  const [messages, setMessages] = useState<{ sender: 'AI' | 'You'; text: string }[]>([
    { sender: 'AI', text: 'Explain your approach before submitting your code.' },
  ]);
  const [aiSpeaking, setAiSpeaking] = useState(false);
  const [isThinking, setIsThinking] = useState(false);

  const { isRecording, startRecording, stopRecording } = useRecorder();
  const navigate = useNavigate();

  const speak = (text: string) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1.05;
    utterance.onstart = () => setAiSpeaking(true);
    utterance.onend = () => setAiSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    fetchWithAuth('http://localhost:5000/api/coding-problem')
      .then((res) => res.json())
      .then((data) => {
        setProblem(data);
        // 🔥 ADDED: Speak the introduction if available
        if (data.spoken_intro) {
           speak(data.spoken_intro);
           setMessages(prev => [...prev, { sender: 'AI', text: data.spoken_intro }]);
        }
      })
      .catch(() => navigate('/interview'));
  }, []);

  const handleRecord = async () => {
    if (!isRecording) {
      await startRecording();
    } else {
      const audioBlob = await stopRecording();
      const formData = new FormData();
      formData.append('audio', audioBlob);

      setIsThinking(true);

      const res = await fetchWithAuth('http://localhost:5000/api/code-explanation', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { sender: 'You', text: data.user_text },
        { sender: 'AI', text: data.response },
      ]);
      speak(data.response);
      setIsThinking(false);
    }
  };

  const handleSubmit = async () => {
    const res = await fetchWithAuth('http://localhost:5000/api/submit-code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    });

    if (res.ok) {
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { sender: 'You', text: 'You submitted your code.' },
        { sender: 'AI', text: 'Now solve the next question.' },
      ]);
      speak(data.feedback);

      if (data.next && data.problem) {
        setProblem(data.problem);
        setCode('');
        // 🔥 ADDED: Speak intro for NEXT problem too
        if (data.problem.spoken_intro) {
            speak(data.problem.spoken_intro);
            setMessages(prev => [...prev, { sender: 'AI', text: data.problem.spoken_intro }]);
        }
      } else {
        navigate('/interview');
      }
    }
  };
  // --- LOGIC END ---

  // --- UI STYLES ---
  const bg = "gray.900";
  const panelBg = "gray.800";
  const editorBg = "#1e1e1e"; // VS Code Dark
  const userBubbleBg = "teal.600";
  const aiBubbleBg = "gray.700";

  return (
    <Box h="100vh" bg={bg} color="white" overflow="hidden">
      
      {/* Header */}
      <Flex h="60px" px={6} align="center" borderBottom="1px solid" borderColor="gray.700" bg={panelBg}>
         <Icon as={FaCode} color="teal.400" mr={3} />
         <Heading size="sm" letterSpacing="wide">LIVE CODING CHALLENGE</Heading>
         {aiSpeaking && <Badge ml={4} colorScheme="green" variant="solid">AI Speaking...</Badge>}
      </Flex>

      <Flex h="calc(100vh - 60px)">
        
        {/* Left: Chat & Problem Description */}
        <Box 
          flex="1" 
          maxW="450px" 
          bg={panelBg} 
          borderRight="1px solid" 
          borderColor="gray.700" 
          display="flex" 
          flexDirection="column"
        >
          {/* Problem Card */}
          <Box p={5} borderBottom="1px solid" borderColor="gray.700" bg="gray.800">
             {problem ? (
               <VStack align="start" spacing={2}>
                 <Heading size="md" color="white">{problem.title}</Heading>
                 <Text fontSize="sm" color="gray.400">{problem.description}</Text>
                 <Code 
                    p={2} 
                    mt={2} 
                    borderRadius="md" 
                    bg="blackAlpha.500" 
                    color="teal.200" 
                    w="100%" 
                    display="block"
                    whiteSpace="pre-wrap"
                 >
                   {problem.function_signature}
                 </Code>
               </VStack>
             ) : (
               <Text color="gray.500">Loading problem...</Text>
             )}
          </Box>

          {/* Transcript Area */}
          <Box flex="1" overflowY="auto" p={4} css={{ '&::-webkit-scrollbar': { display: 'none' } }}>
             <VStack spacing={4} align="stretch">
               {messages.map((msg, i) => (
                 <Flex key={i} direction="column" align={msg.sender === 'You' ? 'flex-end' : 'flex-start'}>
                    <HStack mb={1} spacing={2} flexDirection={msg.sender === 'You' ? 'row-reverse' : 'row'}>
                       <Text fontSize="xs" color="gray.500" fontWeight="bold">
                         {msg.sender === 'You' ? 'You' : 'Interviewer'}
                       </Text>
                    </HStack>
                    <Box
                      bg={msg.sender === 'AI' ? aiBubbleBg : userBubbleBg}
                      px={4} py={3}
                      borderRadius="xl"
                      borderBottomRightRadius={msg.sender === 'You' ? 'none' : 'xl'}
                      borderBottomLeftRadius={msg.sender === 'AI' ? 'none' : 'xl'}
                      maxW="90%"
                      boxShadow="sm"
                    >
                      <Text fontSize="sm">{msg.text}</Text>
                    </Box>
                 </Flex>
               ))}
               
               {isThinking && (
                 <HStack alignSelf="flex-start">
                   <Avatar size="xs" name="AI" bg="purple.500" />
                   <DotTypingAnimation />
                 </HStack>
               )}
             </VStack>
          </Box>

          {/* Bottom Action Bar */}
          <Box p={4} borderTop="1px solid" borderColor="gray.700" bg="gray.900">
             <HStack spacing={4}>
               {/* Recruiter Avatar */}
               <Box position="relative">
                 <RecruiterAvatar isSpeaking={aiSpeaking} />
               </Box>
               
               {/* Record Button */}
               <Button
                 leftIcon={isRecording ? <FaMicrophoneSlash /> : <FaMicrophone />}
                 colorScheme={isRecording ? "red" : "teal"}
                 onClick={handleRecord}
                 isDisabled={aiSpeaking}
                 w="full"
                 size="lg"
                 borderRadius="full"
               >
                 {isRecording ? "Stop Explanation" : "Explain Logic"}
               </Button>
             </HStack>
          </Box>
        </Box>

        {/* Right: Code Editor */}
        <Box flex="2" display="flex" flexDirection="column" bg={editorBg}>
           <Box flex="1" position="relative">
             <Editor
               height="100%"
               defaultLanguage="python"
               value={code}
               onChange={(value) => setCode(value || '')}
               theme="vs-dark"
               options={{
                 fontSize: 16,
                 fontFamily: "'Fira Code', monospace",
                 formatOnType: true,
                 autoIndent: 'full',
                 minimap: { enabled: false },
                 scrollBeyondLastLine: false,
                 padding: { top: 20 }
               }}
             />
           </Box>
           
           {/* Editor Footer */}
           <Flex 
             h="60px" 
             bg="gray.800" 
             borderTop="1px solid" 
             borderColor="gray.700" 
             align="center" 
             justify="flex-end" 
             px={6}
           >
              <Button 
                rightIcon={<FaPlay />} 
                colorScheme="green" 
                size="md" 
                px={8}
                onClick={handleSubmit}
                _hover={{ transform: "translateY(-2px)", boxShadow: "lg" }}
              >
                Submit
              </Button>
           </Flex>
        </Box>
      </Flex>
    </Box>
  );
}