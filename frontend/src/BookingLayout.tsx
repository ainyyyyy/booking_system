import * as React from 'react';
//import Link from '@mui/material/Link';
//import SvgIcon, { type SvgIconProps } from '@mui/material/SvgIcon';
//import Typography from '@mui/material/Typography';
import Header from './components/BookingHeader.tsx';
import { styled } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import MenuItem from '@mui/material/MenuItem';
import Grid from '@mui/material/Grid';
import Divider, { dividerClasses } from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import List from '@mui/material/List';
import Toolbar from '@mui/material/Toolbar';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import InboxIcon from '@mui/icons-material/Inbox';
import ListItemIcon from '@mui/material/ListItemIcon';
import { Outlet } from 'react-router';


// const StyledBox = styled('div')(({ theme }) => ({
//   alignSelf: 'center',
//   width: '100%',
//   height: 400,
//   marginTop: theme.spacing(8),
//   borderRadius: (theme.vars || theme).shape.borderRadius,
//   outline: '6px solid',
//   outlineColor: 'hsla(220, 25%, 80%, 0.2)',
//   border: '1px solid',
//   borderColor: (theme.vars || theme).palette.grey[200],
//   boxShadow: '0 0 12px 8px hsla(220, 25%, 80%, 0.2)',
//   backgroundImage: `https://mui.com'/static/screenshots/material-ui/getting-started/templates/dashboard.jpg`,
//   backgroundSize: 'cover',
//   [theme.breakpoints.up('sm')]: {
//     marginTop: theme.spacing(10),
//     height: 700,
//   },
//   ...theme.applyStyles('dark', {
//     boxShadow: '0 0 24px 12px hsla(210, 100%, 25%, 0.2)',
//     backgroundImage: `https://mui.com/static/screenshots/material-ui/getting-started/templates/dashboard-dark.jpg`,
//     outlineColor: 'hsla(220, 20%, 42%, 0.1)',
//     borderColor: (theme.vars || theme).palette.grey[700],
//   }),
// }));

const drawerWidth = 480;

export default function Layout() {
  return (
    <Box
      sx={(theme) => ({
        display: 'flex',
        '--header-gap': theme.spacing(3.5),
        '--header-spacing': 'calc(var(--template-frame-height, 0px) + 28px)',
        '--header-total-height': 'calc(48px + 2 * var(--header-spacing))',
      })}
    >
      <CssBaseline />
      <Header />
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
        variant="permanent"
        // anchor="left"
      >
        <Box sx={{ height: 'var(--header-total-height)' }} />
        <Container
          maxWidth="lg"
          component="main"
          sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}
        >
          <Box sx={{ overflow: 'auto' }}>
            <List>
              {['Inbox', 'Starred', 'Send email', 'Drafts'].map((text) => (
                <ListItem key={text} disablePadding>
                  <ListItemButton>
                    <ListItemIcon>
                      <InboxIcon />
                    </ListItemIcon>
                    <Typography variant="h5" gutterBottom>
                      {text}
                    </Typography>
                    {/* <ListItemText primary={text} /> */}
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
        </Container>
      </Drawer>
      <Box
        component="main"
        sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` } }}
      >
        <Box sx={{ height: 'var(--header-total-height)' }} />
        <Outlet />
      </Box>
    </Box>
  );
}