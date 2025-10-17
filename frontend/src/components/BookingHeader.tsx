import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import AdbIcon from '@mui/icons-material/Adb';
import { styled, alpha } from '@mui/material/styles';


const StyledToolbar = styled(Toolbar)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  flexShrink: 0,
  borderRadius: `calc(${theme.shape.borderRadius}px + 8px)`,
  backdropFilter: 'blur(24px)',
  border: '1px solid',
  borderColor: (theme.vars || theme).palette.divider,
  backgroundColor: theme.vars
    ? `rgba(${theme.vars.palette.background.defaultChannel} / 0.4)`
    : alpha(theme.palette.background.default, 0.4),
  boxShadow: (theme.vars || theme).shadows[1],
  padding: '8px 12px',
}));

function BookingHeader() {
  return (
    <AppBar
      position="fixed"
      enableColorOnDark
      sx={{
        zIndex: (t) => t.zIndex.drawer + 1,
        boxShadow: 0,
        bgcolor: 'transparent',
        backgroundImage: 'none',
        mt: 'var(--header-spacing)',
      }}
    >
      <Container maxWidth="xl">
        <StyledToolbar variant="dense" disableGutters>
          <AdbIcon sx={{ display: { xs: 'none', md: 'flex' }, mr: 1 }} />
          <Typography
            variant="h4"
            noWrap
            component="div" 
            sx={{ flexGrow: 1 }}
          >
            easybook
          </Typography>
          <Button color="primary" variant="text" size="small">
            Sign in
          </Button>
          <Button color="primary" variant="contained" size="small">
            Sign up
          </Button>
          {/* <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>            
            {pages.map((page) => (
              <Button
                key={page}
                sx={{ my: 2, color: 'white', display: 'block' }}
              >
                {page}
              </Button>
            ))}
          </Box> */}
        </StyledToolbar>
      </Container>
    </AppBar>
  );
}
export default BookingHeader;