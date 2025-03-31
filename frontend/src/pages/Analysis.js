import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import axios from 'axios';

function Analysis() {
  const [transactionId, setTransactionId] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!transactionId) {
      setError('Please enter a transaction ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`http://localhost:8000/analyze-fraud/`, {
        transaction_id: parseInt(transactionId),
      });
      setAnalysisResult(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Error analyzing transaction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Fraud Analysis
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" gap={2} alignItems="center">
              <TextField
                label="Transaction ID"
                value={transactionId}
                onChange={(e) => setTransactionId(e.target.value)}
                type="number"
                sx={{ flexGrow: 1 }}
              />
              <Button
                variant="contained"
                onClick={handleAnalyze}
                disabled={loading}
              >
                Analyze
              </Button>
            </Box>

            {error && (
              <Typography color="error" sx={{ mt: 2 }}>
                {error}
              </Typography>
            )}

            {loading && (
              <Box display="flex" justifyContent="center" mt={3}>
                <CircularProgress />
              </Box>
            )}

            {analysisResult && (
              <Box mt={3}>
                <Typography variant="h6" gutterBottom>
                  Analysis Results
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Fraud Score
                        </Typography>
                        <Typography
                          variant="h4"
                          color={analysisResult.fraud_score > 0.7 ? 'error' : 'primary'}
                        >
                          {(analysisResult.fraud_score * 100).toFixed(2)}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Risk Level
                        </Typography>
                        <Typography variant="h4">
                          {analysisResult.fraud_score > 0.7
                            ? 'High Risk'
                            : analysisResult.fraud_score > 0.3
                            ? 'Medium Risk'
                            : 'Low Risk'}
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

export default Analysis; 