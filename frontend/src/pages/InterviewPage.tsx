import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Button,
  Flex,
  Heading,
  Text,
  VStack,
  Avatar,
  useColorModeValue,
  HStack,
  Badge,
  keyframes,
  Icon,
  Tooltip,
  IconButton,
  Center
} from '@chakra-ui/react';
import { useRecorder } from '../hooks/useRecorder';
import { useNavigate } from 'react-router-dom';
import { fetchWithAuth } from '../utils/fetchWithAuth';
import { useAttentionTracker } from '../hooks/useAttentionTracker';
import RecruiterAvatar from '../components/RecruiterAvatar';
import { 
  FaMicrophone, FaMicrophoneSlash, 
  FaVideo, FaVideoSlash, 
  FaPhoneSlash, FaEye, FaEyeSlash 
} from 'react-icons/fa';

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

export default function InterviewPage() {
  // --- LOGIC START (UNCHANGED CORE) ---
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const attention = useAttentionTracker(videoRef);
  const interviewEndedRef = useRef(false);
  const [aiSpeaking, setAiSpeaking] = useState(false);
  const [showTyping, setShowTyping] = useState(false);
  const [messages, setMessages] = useState<{ sender: 'AI' | 'You'; text: string; confidence?: number }[]>([]);
  const { isRecording, startRecording, stopRecording } = useRecorder();

  // New State for Video Toggle
  const [isVideoOn, setIsVideoOn] = useState(true);

  // 🔥 AUTO-SCROLL REF
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // 🔥 AUTO-SCROLL FUNCTION
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // 🔥 SCROLL EFFECT
  useEffect(() => {
    scrollToBottom();
  }, [messages, showTyping]);

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return "High";
    if (score >= 0.5) return "Medium";
    return "Low";
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "green";
    if (score >= 0.5) return "yellow";
    return "red";
  };

  const handleEndInterview = async () => {
    if (confirm("Are you sure you want to end the interview? You will be taken to the feedback page.")) {
      try {
        window.speechSynthesis.cancel();
        setAiSpeaking(false);
        await fetchWithAuth('http://localhost:5000/api/end-interview', {
          method: 'POST',
        }).catch(() => { });
      } catch (err) {
        console.error('Error ending interview:', err);
      }
      navigate('/feedback');
    }
  };

  const speak = (text: string) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1.05;
    utterance.onstart = () => setAiSpeaking(true);
    utterance.onend = () => setAiSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  const handleRecord = async () => {
    if (!isRecording) {
      await startRecording();
    } else {
      const audioBlob = await stopRecording();
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('focus_score', attention.toString());

      setShowTyping(true);

      try {
        const res = await fetchWithAuth('http://localhost:5000/api/audio', {
          method: 'POST',
          body: formData,
        });

        const { text: aiText, answer: userText, confidence, interview_ended: isInterviewEnded } = await res.json();

        setMessages((prev) => [
          ...prev,
          { sender: 'You', text: userText, confidence },
        ]);

        setTimeout(() => {
          setShowTyping(false);
          setMessages((prev) => [...prev, { sender: 'AI', text: aiText }]);
          speak(aiText);

          if (isInterviewEnded && !interviewEndedRef.current) {
            interviewEndedRef.current = true;
            // Turn off camera when interview ends
            if (videoRef.current?.srcObject) {
              const stream = videoRef.current.srcObject as MediaStream;
              stream.getTracks().forEach(track => track.stop());
              setIsVideoOn(false);
            }
            setTimeout(() => navigate('/feedback'), 2000);
          } else if (aiText.includes("interview is complete") && !interviewEndedRef.current) {
            interviewEndedRef.current = true;
            // Turn off camera when interview ends
            if (videoRef.current?.srcObject) {
              const stream = videoRef.current.srcObject as MediaStream;
              stream.getTracks().forEach(track => track.stop());
              setIsVideoOn(false);
            }
            navigate('/feedback');
          } else if (aiText.toLowerCase().includes("live coding round")) {
            setTimeout(() => navigate("/coding"), 1000);
          } else if (aiText.toLowerCase().includes("behavioral") && !aiText.includes("Thank you")) {
            alert("Now starting the HR round!");
          }
        }, 1500); 
      } catch (err) {
        setShowTyping(false);
        console.error('API Error:', err);
        alert('Error contacting backend');
      }
    }
  };

  useEffect(() => {
    const fetchInitialHistory = async () => {
      try {
        const res = await fetchWithAuth('http://localhost:5000/api/history');
        const data = await res.json();
        if (Array.isArray(data.history) && data.history.length > 0) {
          const formattedMessages = data.history.map((entry: any) => ({
            sender: entry.sender === 'user' ? 'You' : 'AI',
            text: entry.question || entry.answer || '', 
            confidence: entry.confidence || undefined,
          }));
          setMessages(formattedMessages);
          const latestAiMsg = formattedMessages.findLast((m: any) => m.sender === 'AI');
          if (latestAiMsg) speak(latestAiMsg.text);
        }
      } catch (err) {
        console.error("Failed to load initial history:", err);
      }
    };
    fetchInitialHistory();
  }, []);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch((err) => {
        console.error('Webcam error:', err);
        alert('Could not access webcam.');
      });

    return () => {
      if (videoRef.current?.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, []);

  const toggleVideo = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      const videoTrack = stream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoOn(videoTrack.enabled);
      }
    }
  };
  // --- LOGIC END ---

  // --- UI STYLES ---
  const bg = "gray.900"; 
  const panelBg = "gray.800";
  const userBubbleBg = "teal.600";
  const aiBubbleBg = "gray.700";

  return (
    <Box h="100vh" bg={bg} overflow="hidden" color="white">
      
      {/* Header */}
      <Flex 
        h="60px" 
        bg="gray.800" 
        px={6} 
        align="center" 
        justify="space-between" 
        borderBottom="1px solid" 
        borderColor="gray.700"
      >
        <HStack spacing={3}>
           <Icon as={FaVideo} color="teal.400" />
           <Heading size="sm" letterSpacing="wide">LIVE INTERVIEW SESSION</Heading>
           {aiSpeaking && <Badge colorScheme="green" variant="solid" ml={2}>AI Speaking...</Badge>}
        </HStack>
        
        <Button
          leftIcon={<FaPhoneSlash />}
          colorScheme="red"
          size="sm"
          variant="solid"
          onClick={handleEndInterview}
          borderRadius="full"
          px={6}
        >
          End Call
        </Button>
      </Flex>

      <Flex h="calc(100vh - 60px)">
        
        {/* Left: Video Area */}
        <Box flex="3" position="relative" bg="black" display="flex" flexDirection="column" justify="center">
          
          {/* User Video Feed */}
          <Box position="relative" w="100%" h="100%" overflow="hidden">
             <video 
               ref={videoRef} 
               style={{ 
                 width: '100%', 
                 height: '100%', 
                 objectFit: 'cover', 
                 transform: 'scaleX(-1)',
                 display: isVideoOn ? 'block' : 'none' 
               }} 
               autoPlay 
               muted 
               playsInline 
             />
             
             {!isVideoOn && (
               <Center w="100%" h="100%" bg="gray.900">
                 <VStack spacing={4}>
                    <Avatar size="2xl" name="You" bg="teal.600" />
                    <Text color="gray.400">Camera is turned off</Text>
                 </VStack>
               </Center>
             )}
             
             <Box position="absolute" top={6} right={6} zIndex={10}>
               <RecruiterAvatar isSpeaking={aiSpeaking} />
             </Box>

             <Box 
               position="absolute" bottom={6} left={6} 
               bg="blackAlpha.700" backdropFilter="blur(10px)" px={4} py={2} borderRadius="lg"
               display="flex" alignItems="center" gap={3}
             >
               <Text fontWeight="bold" fontSize="sm">You (Candidate)</Text>
               <HStack spacing={1}>
                  <Icon as={attention ? FaEye : FaEyeSlash} color={attention ? "green.400" : "red.400"} boxSize={3} />
                  <Text fontSize="xs" color={attention ? "green.200" : "red.200"}>
                    {attention ? "Focused" : "Distracted"}
                  </Text>
               </HStack>
             </Box>
          </Box>

          {/* Controls Bar */}
          <Flex 
            position="absolute" bottom="30px" left="50%" transform="translateX(-50%)" 
            gap={6} align="center" bg="blackAlpha.800" backdropFilter="blur(12px)" p={4} px={8}
            borderRadius="2xl" boxShadow="2xl" border="1px solid" borderColor="whiteAlpha.200"
          >
             <Tooltip label={isVideoOn ? "Turn Camera Off" : "Turn Camera On"}>
                <IconButton 
                   aria-label="Toggle Video" 
                   icon={isVideoOn ? <FaVideo /> : <FaVideoSlash />}
                   onClick={toggleVideo}
                   isRound size="lg" variant="ghost" color={isVideoOn ? "white" : "red.400"}
                   _hover={{ bg: "whiteAlpha.200" }}
                />
             </Tooltip>

             <Button
                leftIcon={isRecording ? <FaMicrophoneSlash /> : <FaMicrophone />}
                colorScheme={isRecording ? "red" : "teal"}
                size="lg" height="56px" fontSize="lg"
                onClick={handleRecord}
                isDisabled={aiSpeaking}
                isLoading={aiSpeaking}
                loadingText="AI Speaking..."
                borderRadius="full" px={8}
                boxShadow={isRecording ? "0 0 20px rgba(245, 101, 101, 0.6)" : "0 0 20px rgba(56, 178, 172, 0.4)"}
                _hover={{ transform: 'scale(1.05)' }}
                transition="all 0.2s"
             >
               {isRecording ? "Stop Recording" : "Start Speaking"}
             </Button>

             <IconButton 
               aria-label="Settings" icon={<Icon as={FaEye} />} 
               isRound size="lg" variant="ghost" color="whiteAlpha.600" 
             />
          </Flex>
        </Box>

        {/* Right: Transcript Panel */}
        <Box 
          flex="1" maxW="400px" bg={panelBg} borderLeft="1px solid" borderColor="gray.700" 
          display="flex" flexDirection="column"
        >
          <Box p={4} borderBottom="1px solid" borderColor="gray.700">
             <Heading size="xs" color="gray.400" textTransform="uppercase">Transcript History</Heading>
          </Box>

          <VStack 
            flex="1" overflowY="auto" spacing={4} p={4} align="stretch"
            css={{
              '&::-webkit-scrollbar': { width: '4px' },
              '&::-webkit-scrollbar-track': { width: '6px' },
              '&::-webkit-scrollbar-thumb': { background: '#555', borderRadius: '24px' },
            }}
          >
            {messages.map((msg, i) => (
              <Flex key={i} direction="column" align={msg.sender === 'You' ? 'flex-end' : 'flex-start'}>
                <HStack mb={1} spacing={2} flexDirection={msg.sender === 'You' ? 'row-reverse' : 'row'}>
                   <Text fontSize="xs" color="gray.500" fontWeight="bold">
                     {msg.sender === 'You' ? 'You' : 'Recruiter'}
                   </Text>
                </HStack>

                <Box
                  bg={msg.sender === 'AI' ? aiBubbleBg : userBubbleBg}
                  color="white" px={4} py={3} borderRadius="2xl"
                  borderBottomRightRadius={msg.sender === 'You' ? 'none' : '2xl'}
                  borderBottomLeftRadius={msg.sender === 'AI' ? 'none' : '2xl'}
                  maxW="90%" boxShadow="md"
                >
                  <Text fontSize="sm" lineHeight="tall">{msg.text}</Text>
                </Box>

                {msg.sender === 'You' && msg.confidence !== undefined && (
                  <Badge mt={1} colorScheme={getConfidenceColor(msg.confidence)} variant="subtle" size="sm" fontSize="10px">
                    Confidence: {getConfidenceLabel(msg.confidence)}
                  </Badge>
                )}
              </Flex>
            ))}

            {showTyping && (
               <Flex align="center" gap={2}>
                 <Avatar size="xs" name="AI" src="" bg="purple.500" />
                 <DotTypingAnimation />
               </Flex>
            )}
            
            {/* 🔥 DUMMY DIV FOR AUTO-SCROLL TARGET */}
            <div ref={messagesEndRef} />
          </VStack>
        </Box>
      </Flex>
    </Box>
  );
}