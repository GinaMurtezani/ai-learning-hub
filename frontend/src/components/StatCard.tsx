import { useEffect, useRef, useState } from 'react';
import { Box, Card, Typography } from '@mui/material';
import { motion } from 'framer-motion';

function easeOutCubic(t: number) {
  return 1 - Math.pow(1 - t, 3);
}

function useCountUp(target: number, duration = 400) {
  const [value, setValue] = useState(0);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    const start = performance.now();
    function tick(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      setValue(Math.round(easeOutCubic(progress) * target));
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }, [target, duration]);

  return value;
}

interface StatCardProps {
  emoji: string;
  label: string;
  value: number;
  suffix: string;
  color: string;
  /** If provided, shown instead of the animated number */
  displayOverride?: (animatedValue: number) => string;
}

export default function StatCard({ emoji, label, value, suffix, color, displayOverride }: StatCardProps) {
  const animatedValue = useCountUp(value);

  return (
    <Card
      component={motion.div}
      whileHover={{ y: -2 }}
      sx={{
        position: 'relative',
        overflow: 'hidden',
        p: 3,
        cursor: 'default',
        transition: 'box-shadow 0.2s',
        '&:hover': {
          boxShadow: `0 8px 24px ${color}33`,
        },
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(circle at top right, ${color}22 0%, transparent 70%)`,
          pointerEvents: 'none',
        }}
      />
      <Box sx={{ position: 'relative' }}>
        <Typography variant="h4" sx={{ mb: 0.5 }}>
          {emoji}
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
          {label}
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 700, color }}>
          {displayOverride ? displayOverride(animatedValue) : animatedValue}
          <Typography component="span" variant="body1" sx={{ ml: 1, color: 'text.secondary', fontWeight: 400 }}>
            {suffix}
          </Typography>
        </Typography>
      </Box>
    </Card>
  );
}
