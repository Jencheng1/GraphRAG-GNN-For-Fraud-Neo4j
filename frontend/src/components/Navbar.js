import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Receipt as ReceiptIcon,
  Analytics as AnalyticsIcon,
  School as SchoolIcon,
} from '@mui/icons-material';

function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Credit Fraud Detection
        </Typography>
        <Box>
          <Button
            color="inherit"
            component={RouterLink}
            to="/"
            startIcon={<DashboardIcon />}
          >
            Dashboard
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/transactions"
            startIcon={<ReceiptIcon />}
          >
            Transactions
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/analysis"
            startIcon={<AnalyticsIcon />}
          >
            Analysis
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/training"
            startIcon={<SchoolIcon />}
          >
            Training
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar; 