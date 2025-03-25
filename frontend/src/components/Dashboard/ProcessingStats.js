import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Divider,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Assignment as AssignmentIcon,
  AssignmentTurnedIn as AssignmentTurnedInIcon,
  AssignmentLate as AssignmentLateIcon,
  HourglassEmpty as HourglassEmptyIcon,
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { processingAPI } from '../../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

// Estimated time in minutes for each processing stage
const PROCESSING_TIME_ESTIMATES = {
  file_upload: 1,
  data_extraction: 3,
  validation: 2,
  document_generation: 5,
  pdf_conversion: 2
};

function ProcessingStats() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    activeJobs: 0,
    completedJobs: 0,
    failedJobs: 0,
    totalDocuments: 0,
    processingStages: []
  });
  const [recentJobs, setRecentJobs] = useState([]);
  const [processingTimeData, setProcessingTimeData] = useState([]);

  useEffect(() => {
    fetchData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch processing statistics
      const statsResponse = await processingAPI.getProcessingStats();
      setStats(statsResponse.data);

      // Fetch recent jobs
      const jobsResponse = await processingAPI.getJobs();
      setRecentJobs(jobsResponse.data.slice(0, 5)); // Get the 5 most recent jobs

      // Prepare processing time data for chart
      const timeData = Object.entries(PROCESSING_TIME_ESTIMATES).map(([stage, time]) => ({
        name: formatStageName(stage),
        time: time
      }));
      setProcessingTimeData(timeData);

      setLoading(false);
    } catch (err) {
      console.error('Error fetching processing stats:', err);
      setError('Failed to load processing statistics. Please try again.');
      setLoading(false);
    }
  };

  const formatStageName = (stage) => {
    return stage
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getJobStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getJobStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <AssignmentTurnedInIcon />;
      case 'processing':
        return <HourglassEmptyIcon />;
      case 'failed':
        return <AssignmentLateIcon />;
      default:
        return <AssignmentIcon />;
    }
  };

  const calculateEstimatedTime = (job) => {
    if (job.status === 'completed' || job.status === 'failed') {
      return 'Finished';
    }

    // Get current stage
    const currentStage = job.current_stage || 'file_upload';
    
    // Calculate remaining time based on current stage
    let remainingTime = 0;
    let foundCurrentStage = false;
    
    for (const [stage, time] of Object.entries(PROCESSING_TIME_ESTIMATES)) {
      if (stage === currentStage) {
        foundCurrentStage = true;
        // Add half of the current stage time (assuming we're halfway through)
        remainingTime += time / 2;
        continue;
      }
      
      if (foundCurrentStage) {
        // Add full time for stages we haven't reached yet
        remainingTime += time;
      }
    }
    
    // Format the remaining time
    if (remainingTime < 1) {
      return 'Less than a minute';
    } else if (remainingTime === 1) {
      return 'About 1 minute';
    } else {
      return `About ${Math.round(remainingTime)} minutes`;
    }
  };

  const getProgressPercentage = (job) => {
    if (job.status === 'completed') return 100;
    if (job.status === 'failed') return 100;
    
    const stages = ['file_upload', 'data_extraction', 'validation', 'document_generation', 'pdf_conversion'];
    const currentStageIndex = stages.indexOf(job.current_stage || 'file_upload');
    
    if (currentStageIndex === -1) return 0;
    
    // Calculate progress as percentage of completed stages plus half of current stage
    return Math.min(100, Math.round((currentStageIndex / stages.length) * 100) + 10);
  };

  if (loading && !stats.activeJobs) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <HourglassEmptyIcon color="warning" sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="h4">{stats.activeJobs}</Typography>
                  <Typography variant="body2" color="textSecondary">Active Jobs</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AssignmentTurnedInIcon color="success" sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="h4">{stats.completedJobs}</Typography>
                  <Typography variant="body2" color="textSecondary">Completed Jobs</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <DescriptionIcon color="primary" sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="h4">{stats.totalDocuments}</Typography>
                  <Typography variant="body2" color="textSecondary">Generated Documents</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Processing Time Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Estimated Processing Time by Stage
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={processingTimeData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis label={{ value: 'Minutes', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="time" fill="#8884d8" name="Time (minutes)" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Processing Stages Distribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Processing Stages Distribution
            </Typography>
            <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
              {stats.processingStages.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={stats.processingStages}
                      cx="50%"
                      cy="50%"
                      labelLine={true}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                      nameKey="stage"
                      label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    >
                      {stats.processingStages.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value, name) => [`${value} jobs`, name]} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography variant="body1" color="textSecondary">
                    No active processing jobs
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Recent Jobs */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Processing Jobs
            </Typography>
            <Box>
              {recentJobs.length > 0 ? (
                recentJobs.map((job) => (
                  <Box key={job.id} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ mr: 2 }}>
                        {getJobStatusIcon(job.status)}
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle1">
                            Job #{job.id} - {new Date(job.created_at).toLocaleString()}
                          </Typography>
                          <Chip
                            label={job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                            color={getJobStatusColor(job.status)}
                            size="small"
                          />
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                          <Typography variant="body2" color="textSecondary">
                            Current Stage: {job.current_stage ? formatStageName(job.current_stage) : 'N/A'}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            Estimated Time: {calculateEstimatedTime(job)}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={getProgressPercentage(job)}
                      color={job.status === 'failed' ? 'error' : 'primary'}
                      sx={{ height: 8, borderRadius: 5 }}
                    />
                    <Divider sx={{ mt: 2 }} />
                  </Box>
                ))
              ) : (
                <Typography variant="body1" color="textSecondary">
                  No recent jobs found
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default ProcessingStats;
