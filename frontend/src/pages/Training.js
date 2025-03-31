import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import axios from 'axios';

function Training() {
  const [loading, setLoading] = useState(false);
  const [trainingResult, setTrainingResult] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const handleTrain = async () => {
    setLoading(true);
    setError(null);
    setProgress(0);

    try {
      const response = await axios.post('http://localhost:8000/train-gnn/');
      setTrainingResult(response.data);
      
      // Simulate progress updates
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setProgress(i);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Error training the model');
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Model Training
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6">
                Train GNN Model
              </Typography>
              <Button
                variant="contained"
                color="primary"
                onClick={handleTrain}
                disabled={loading}
              >
                Start Training
              </Button>
            </Box>

            {error && (
              <Typography color="error" sx={{ mt: 2 }}>
                {error}
              </Typography>
            )}

            {loading && (
              <Box mt={3}>
                <Typography variant="body1" gutterBottom>
                  Training in progress...
                </Typography>
                <LinearProgress variant="determinate" value={progress} />
                <Typography variant="body2" color="textSecondary" align="right" mt={1}>
                  {progress}%
                </Typography>
              </Box>
            )}

            {trainingResult && (
              <Box mt={3}>
                <Typography variant="h6" gutterBottom>
                  Training Results
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Status
                        </Typography>
                        <Typography variant="h4" color="success.main">
                          {trainingResult.status}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Final Loss
                        </Typography>
                        <Typography variant="h4">
                          {trainingResult.results.final_loss.toFixed(4)}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Training; 