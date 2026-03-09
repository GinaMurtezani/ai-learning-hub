import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  Leaderboard as LeaderboardIcon,
  Person as PersonIcon,
  EmojiEvents as EmojiEventsIcon,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material';

const SIDEBAR_WIDTH = 280;
const SIDEBAR_COLLAPSED = 72;

const NAV_ITEMS = [
  { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
  { label: 'Lernpfade', path: '/learn', icon: <SchoolIcon /> },
  { label: 'Leaderboard', path: '/leaderboard', icon: <LeaderboardIcon /> },
  { label: 'Achievements', path: '/achievements', icon: <EmojiEventsIcon /> },
  { label: 'AI Chat', path: '/chat', icon: <SmartToyIcon /> },
  { label: 'Profil', path: '/profile', icon: <PersonIcon /> },
];

export default function DashboardLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const drawerWidth = collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_WIDTH;

  const isActive = (path: string) =>
    path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: `calc(100% - ${drawerWidth}px)`,
          ml: `${drawerWidth}px`,
          bgcolor: 'background.paper',
          backgroundImage: 'none',
          borderBottom: '1px solid',
          borderColor: 'divider',
          boxShadow: 'none',
          transition: 'width 0.3s ease, margin-left 0.3s ease',
        }}
      >
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => setCollapsed(!collapsed)}
            sx={{ mr: 2 }}
          >
            {collapsed ? <MenuIcon /> : <ChevronLeftIcon />}
          </IconButton>
          <Typography variant="h6" noWrap sx={{ color: 'text.primary' }}>
            AI Learning Hub
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          transition: 'width 0.3s ease',
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: '#212B36',
            borderRight: '1px dashed',
            borderColor: 'divider',
            transition: 'width 0.3s ease',
            overflowX: 'hidden',
          },
        }}
      >
        <Toolbar>
          {!collapsed && (
            <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 700 }}>
              AI Hub
            </Typography>
          )}
        </Toolbar>

        <List sx={{ px: 1 }}>
          {NAV_ITEMS.map((item) => {
            const active = isActive(item.path);
            return (
              <ListItemButton
                key={item.path}
                selected={active}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 1,
                  mb: 0.5,
                  py: 1,
                  pl: active ? 1.5 : 2,
                  position: 'relative',
                  transition: 'all 0.2s ease',
                  // Active indicator — vertical bar
                  '&::before': active
                    ? {
                        content: '""',
                        position: 'absolute',
                        left: 0,
                        top: 8,
                        bottom: 8,
                        width: 3,
                        borderRadius: 1.5,
                        bgcolor: 'primary.main',
                      }
                    : {},
                  // Active state
                  '&.Mui-selected': {
                    bgcolor: 'rgba(0, 167, 111, 0.10)',
                    color: 'primary.main',
                    '& .MuiListItemIcon-root': { color: 'primary.main' },
                    '&:hover': {
                      bgcolor: 'rgba(0, 167, 111, 0.16)',
                    },
                  },
                  // Hover state
                  '&:not(.Mui-selected):hover': {
                    bgcolor: 'rgba(255, 255, 255, 0.06)',
                    transform: 'translateY(-1px)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: collapsed ? 'unset' : 40,
                    justifyContent: 'center',
                    color: active ? 'primary.main' : 'text.secondary',
                    transition: 'color 0.2s ease',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {!collapsed && (
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{
                      fontSize: 14,
                      fontWeight: active ? 600 : 400,
                    }}
                  />
                )}
              </ListItemButton>
            );
          })}
        </List>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          bgcolor: 'background.default',
          minHeight: '100vh',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
