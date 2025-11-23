import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  CircularProgress,
  CircularProgressLabel,
  SimpleGrid,
  useColorModeValue,
  Spinner,
  Container,
  Flex,
  Icon,
  Badge,
  Divider,
  HStack
} from '@chakra-ui/react'
import { useEffect, useState } from 'react'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip as RechartsTooltip
} from 'recharts'
import { fetchWithAuth } from '../utils/fetchWithAuth'
import { FaBrain, FaCode, FaUserTie, FaCheckCircle, FaRedo, FaMicrophoneAlt, FaEye } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'

// --- HELPER COMPONENTS ---

const ScoreCard = ({ label, value, color, icon, suffix = "" }: any) => {
  const bg = useColorModeValue("white", "gray.800")
  return (
    <Box bg={bg} p={6} borderRadius="xl" boxShadow="md" borderTop="4px solid" borderColor={color} textAlign="center">
      <Flex justify="center" align="center" mb={3} color={color}>
         <Icon as={icon} boxSize={6} mr={2} />
         <Text fontSize="lg" fontWeight="bold" color="gray.600">{label}</Text>
      </Flex>
      <CircularProgress value={value} color={color} size="120px" thickness="8px">
        <CircularProgressLabel fontSize="xl" fontWeight="bold">
           {suffix ? `${(value).toFixed(0)}${suffix}` : (value / 20).toFixed(1)}
        </CircularProgressLabel>
      </CircularProgress>
      <Text mt={3} fontSize="sm" color="gray.500">
         {value >= 80 ? "Excellent" : value >= 60 ? "Good" : "Needs Practice"}
      </Text>
    </Box>
  )
}

const renderRadarChart = (data: any, color: string) => {
  const chartData =
    data.correctness !== undefined
      ? [
          { metric: 'Correctness', value: data.correctness },
          { metric: 'Clarity', value: data.clarity },
          { metric: 'Edge Cases', value: data.edge_cases },
          { metric: 'Efficiency', value: data.efficiency },
          { metric: 'Overall', value: data.overall },
        ]
      : [
          { metric: 'Relevance', value: data.relevance },
          { metric: 'Clarity', value: data.clarity },
          { metric: 'Depth', value: data.depth },
          { metric: 'Examples', value: data.examples },
          { metric: 'Communication', value: data.communication },
          { metric: 'Overall', value: data.overall },
        ]

  return (
    <Box w="100%" h="320px">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis dataKey="metric" tick={{ fill: '#718096', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 5]} tick={false} axisLine={false} />
          <Radar
            name="Score"
            dataKey="value"
            stroke={color}
            fill={color}
            fillOpacity={0.4}
          />
          <RechartsTooltip />
        </RadarChart>
      </ResponsiveContainer>
    </Box>
  )
}

export default function FeedbackPage() {
  const [feedback, setFeedback] = useState<any | null>(null)
  const navigate = useNavigate()
  
  // Theme Colors
  const bg = useColorModeValue("gray.50", "gray.900")
  const cardBg = useColorModeValue("white", "gray.800")
  const sectionBorder = useColorModeValue("gray.200", "gray.700")

  useEffect(() => {
    let didFetch = false;
    const fetchFeedback = async () => {
      if (didFetch) return;
      didFetch = true;
      try {
        const res = await fetchWithAuth('http://localhost:5000/api/feedback');
        const data = await res.json();
        setFeedback(data);
      } catch (error) {
         console.error("Error fetching feedback:", error)
      }
    };
    fetchFeedback();
  }, []);

  const renderSection = (title: string, icon: any, color: string, data: any) => (
    <Box
      bg={cardBg}
      borderRadius="2xl"
      boxShadow="lg"
      overflow="hidden"
      mb={8}
      border="1px solid"
      borderColor={sectionBorder}
    >
      <Box bg={color} p={4} color="white">
        <HStack spacing={3}>
           <Icon as={icon} boxSize={6} />
           <Heading size="md">{title}</Heading>
        </HStack>
      </Box>
      
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8} p={8} alignItems="center">
        {/* Left: Chart */}
        <Box>
           <Heading size="xs" color="gray.500" mb={4} textAlign="center" textTransform="uppercase" letterSpacing="wide">
             Performance Metrics
           </Heading>
           {renderRadarChart(data, color)}
        </Box>

        {/* Right: Text Summary */}
        <VStack align="stretch" spacing={4}>
           <Box>
             <Text fontWeight="bold" fontSize="lg" color="gray.700" mb={2}>
               <Icon as={FaCheckCircle} color={color} mr={2} />
               Key Takeaways
             </Text>
             <Box 
               p={4} 
               bg={useColorModeValue(`${color}.50`, "whiteAlpha.50")} 
               borderRadius="lg" 
               borderLeft="4px solid" 
               borderColor={color}
             >
               <Text fontSize="md" lineHeight="tall" color="gray.600">
                 {data.summary || "No specific summary available for this section."}
               </Text>
             </Box>
           </Box>
        </VStack>
      </SimpleGrid>
    </Box>
  )

  return (
    <Box minH="100vh" bg={bg} py={12}>
      <Container maxW="container.lg">
        
        {/* Header */}
        <VStack spacing={2} mb={10} textAlign="center">
          <Heading size="2xl" color="gray.700">Interview Report</Heading>
          <Text fontSize="lg" color="gray.500">
             Comprehensive analysis of your AI interview session.
          </Text>
        </VStack>

        {!feedback ? (
          <Flex direction="column" align="center" justify="center" minH="400px" bg={cardBg} borderRadius="xl" boxShadow="sm">
            <Spinner size="xl" color="teal.500" thickness="4px" speed="0.8s" />
            <Text mt={6} fontSize="lg" color="gray.500" fontWeight="medium">Analyzing your performance...</Text>
          </Flex>
        ) : (
          <VStack spacing={8} align="stretch" animation="fadeIn 0.5s ease-in-out">
            
            {/* Top Metrics Row */}
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
              <ScoreCard 
                label="Average Confidence" 
                value={feedback.average_confidence * 20} // Convert 5 scale to 100
                color="blue.400" 
                icon={FaMicrophoneAlt} 
              />
              <ScoreCard 
                label="Average Focus" 
                value={feedback.average_focus * 100} 
                color="green.400" 
                icon={FaEye} 
                suffix="%" 
              />
            </SimpleGrid>

            <Divider my={4} />

            {/* Feedback Sections */}
            {feedback.technical && renderSection('Technical Assessment', FaBrain, 'teal.500', feedback.technical)}
            {feedback.coding && renderSection('Coding Challenge', FaCode, 'purple.500', feedback.coding)}
            {feedback.behavioral && renderSection('Behavioral (HR) Fit', FaUserTie, 'orange.400', feedback.behavioral)}

            {/* Fallback for Custom/Single Rounds */}
            {!('technical' in feedback) && !('coding' in feedback) && !('behavioral' in feedback) && feedback.summary && 
               renderSection('Session Feedback', FaCheckCircle, 'blue.500', feedback)
            }

            {/* Action Footer */}
            <Box textAlign="center" pt={8}>
              <Button
                rightIcon={<FaRedo />}
                colorScheme="teal"
                size="lg"
                height="60px"
                px={10}
                fontSize="xl"
                boxShadow="xl"
                _hover={{ transform: 'translateY(-2px)', boxShadow: '2xl' }}
                onClick={() => navigate('/dashboard')}
              >
                Back to Dashboard
              </Button>
            </Box>

          </VStack>
        )}
      </Container>
    </Box>
  )
}