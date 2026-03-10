import { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CircularProgress,
  Grid,
  Typography,
} from '@mui/material';
import { BarChart as BarChartIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { fetchAnalytics } from '../api/endpoints';

// ── Types ────────────────────────────────────────────────────

interface AnalyticsData {
  overview: {
    total_users: number;
    active_users_today: number;
    total_lessons_completed: number;
    total_chat_messages: number;
    total_xp_earned: number;
    average_level: number;
  };
  xp_distribution: { range: string; count: number }[];
  popular_lessons: {
    title: string;
    path_title: string;
    completions: number;
    chat_messages: number;
  }[];
  path_progress: {
    title: string;
    icon: string;
    total_lessons: number;
    avg_completion_percent: number;
  }[];
  activity_last_7_days: {
    date: string;
    lessons_completed: number;
    chat_messages: number;
  }[];
  achievements_summary: {
    total: number;
    unlocked_by_anyone: number;
    most_common: { name: string; icon: string; unlock_count: number } | null;
    rarest: { name: string; icon: string; unlock_count: number } | null;
  };
  chat_stats: {
    total_messages: number;
    avg_messages_per_lesson: number;
    most_active_lesson: { title: string; message_count: number } | null;
    agent_usage: { agent: string; icon: string; messages: number }[];
  };
}

// ── Helpers ──────────────────────────────────────────────────

const WEEKDAYS = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];

function formatDay(dateStr: string) {
  const d = new Date(dateStr + 'T00:00:00');
  return WEEKDAYS[d.getDay()];
}

const TOOLTIP_STYLE = {
  backgroundColor: '#212B36',
  border: 'none',
  borderRadius: 8,
  color: '#fff',
  fontSize: 12,
};

const GRID_STROKE = 'rgba(255,255,255,0.08)';
const AXIS_STROKE = '#919EAB';

const DONUT_COLORS = ['#00A76F', '#FFB020', '#8E33FF', '#00B8D9', '#FF5630'];

// ── Animation variants ───────────────────────────────────────

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

// ── AnimatedValue ────────────────────────────────────────────

function AnimatedValue({ value, decimals = 0 }: { value: number; decimals?: number }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const start = performance.now();
    const duration = 600;
    function tick(now: number) {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setDisplay(Number((eased * value).toFixed(decimals)));
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }, [value, decimals]);
  return <>{decimals > 0 ? display.toFixed(decimals) : display}</>;
}

// ── Mini StatCard ────────────────────────────────────────────

function MiniStat({
  emoji,
  label,
  value,
  suffix,
  color,
  decimals = 0,
}: {
  emoji: string;
  label: string;
  value: number;
  suffix?: string;
  color: string;
  decimals?: number;
}) {
  return (
    <Card
      sx={{
        p: 2.5,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(circle at top right, ${color}18 0%, transparent 70%)`,
          pointerEvents: 'none',
        }}
      />
      <Box sx={{ position: 'relative' }}>
        <Typography sx={{ fontSize: 22, mb: 0.5 }}>{emoji}</Typography>
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          {label}
        </Typography>
        <Typography variant="h5" sx={{ fontWeight: 700, color, mt: 0.5 }}>
          <AnimatedValue value={value} decimals={decimals} />
          {suffix && (
            <Typography component="span" variant="body2" sx={{ ml: 0.5, color: 'text.secondary', fontWeight: 400 }}>
              {suffix}
            </Typography>
          )}
        </Typography>
      </Box>
    </Card>
  );
}

// ── Main Component ───────────────────────────────────────────

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', pt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!data) {
    return <Typography color="error">Analytics konnten nicht geladen werden.</Typography>;
  }

  const { overview, xp_distribution, popular_lessons, path_progress, activity_last_7_days, achievements_summary, chat_stats } = data;

  const activityData = activity_last_7_days.map((d) => ({
    ...d,
    day: formatDay(d.date),
  }));

  const lessonBarData = popular_lessons.slice(0, 5).map((l) => ({
    ...l,
    shortTitle: l.title.length > 25 ? l.title.slice(0, 22) + '...' : l.title,
  }));

  // Build donut data — use agent_usage if available, else fall back to chat_stats
  const donutData = chat_stats.agent_usage.length > 0
    ? chat_stats.agent_usage.map((a) => ({ name: `${a.icon} ${a.agent}`, value: a.messages }))
    : [{ name: 'Chat', value: chat_stats.total_messages }];

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={{ hidden: {}, show: { transition: { staggerChildren: 0.08 } } }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
        <BarChartIcon sx={{ fontSize: 32, color: '#00B8D9' }} />
        <Typography variant="h4" fontWeight={700}>
          Analytics Dashboard
        </Typography>
      </Box>
      <Typography variant="body2" sx={{ color: 'text.secondary', mb: 4 }}>
        Uebersicht ueber alle Lernaktivitaeten
      </Typography>

      {/* Zone 1 — Overview StatCards */}
      <Grid
        container
        spacing={2}
        sx={{ mb: 4 }}
        component={motion.div}
        variants={container}
        initial="hidden"
        animate="show"
      >
        {[
          { emoji: '\u{1F465}', label: 'Aktive Nutzer', value: overview.total_users, color: '#8E33FF' },
          { emoji: '\u{1F4DA}', label: 'Lektionen abgeschlossen', value: overview.total_lessons_completed, color: '#00A76F' },
          { emoji: '\u{1F4AC}', label: 'Chat-Nachrichten', value: overview.total_chat_messages, color: '#00B8D9' },
          { emoji: '\u26A1', label: 'XP verteilt', value: overview.total_xp_earned, color: '#FFC107' },
          { emoji: '\u{1F4C8}', label: '\u00D8 Level', value: overview.average_level, color: '#FF5630', decimals: 1 },
          {
            emoji: '\u{1F3C6}',
            label: 'Achievements',
            value: achievements_summary.unlocked_by_anyone,
            suffix: `/ ${achievements_summary.total}`,
            color: '#8E33FF',
          },
        ].map((card) => (
          <Grid size={{ xs: 6, sm: 4, md: 2 }} key={card.label} component={motion.div} variants={fadeUp}>
            <MiniStat {...card} />
          </Grid>
        ))}
      </Grid>

      {/* Zone 2 — Charts row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Activity last 7 days */}
        <Grid size={{ xs: 12, md: 7 }} component={motion.div} variants={fadeUp}>
          <Card sx={{ p: 3 }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Aktivitaet letzte 7 Tage
            </Typography>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={activityData}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
                <XAxis dataKey="day" stroke={AXIS_STROKE} fontSize={12} />
                <YAxis stroke={AXIS_STROKE} fontSize={12} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Legend wrapperStyle={{ fontSize: 12, color: AXIS_STROKE }} />
                <Area
                  type="monotone"
                  dataKey="lessons_completed"
                  name="Lektionen"
                  stroke="#00A76F"
                  fill="#00A76F"
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="chat_messages"
                  name="Chat-Nachrichten"
                  stroke="#00B8D9"
                  fill="#00B8D9"
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        {/* Popular Lessons */}
        <Grid size={{ xs: 12, md: 5 }} component={motion.div} variants={fadeUp}>
          <Card sx={{ p: 3 }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Beliebteste Lektionen
            </Typography>
            {lessonBarData.length === 0 ? (
              <Typography variant="body2" sx={{ color: 'text.secondary', py: 4, textAlign: 'center' }}>
                Noch keine Daten
              </Typography>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={lessonBarData} layout="vertical" margin={{ left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} horizontal={false} />
                  <XAxis type="number" stroke={AXIS_STROKE} fontSize={12} />
                  <YAxis
                    dataKey="shortTitle"
                    type="category"
                    width={130}
                    stroke={AXIS_STROKE}
                    fontSize={11}
                    tick={{ fill: AXIS_STROKE }}
                  />
                  <Tooltip
                    contentStyle={TOOLTIP_STYLE}
                    formatter={(value: number, name: string) => [value, name === 'completions' ? 'Abschl\u00fcsse' : name]}
                    labelFormatter={(label: string) => {
                      const item = lessonBarData.find((l) => l.shortTitle === label);
                      return item ? `${item.title} (${item.path_title})` : label;
                    }}
                  />
                  <Bar dataKey="completions" name="Abschl\u00fcsse" fill="#00A76F" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Grid>
      </Grid>

      {/* Zone 3 — Path Progress + Agent Usage */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Path Progress */}
        <Grid size={{ xs: 12, md: 7 }} component={motion.div} variants={fadeUp}>
          <Card sx={{ p: 3 }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Lernpfad-Fortschritt (\u00D8 aller Nutzer)
            </Typography>
            {path_progress.length === 0 ? (
              <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center', py: 4 }}>
                Keine Lernpfade
              </Typography>
            ) : (
              <Box>
                {path_progress.map((path) => (
                  <Box key={path.title} sx={{ mb: 2.5, '&:last-child': { mb: 0 } }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography>{path.icon}</Typography>
                        <Typography variant="body2" fontWeight={600}>{path.title}</Typography>
                      </Box>
                      <Typography variant="body2" fontWeight={700} sx={{ color: '#00A76F' }}>
                        {path.avg_completion_percent}%
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        bgcolor: 'rgba(255,255,255,0.06)',
                        overflow: 'hidden',
                      }}
                    >
                      <Box
                        sx={{
                          height: '100%',
                          width: `${path.avg_completion_percent}%`,
                          borderRadius: 4,
                          bgcolor: '#00A76F',
                          transition: 'width 1s ease',
                        }}
                      />
                    </Box>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {path.total_lessons} Lektionen
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}
          </Card>
        </Grid>

        {/* Agent Usage / Chat Donut */}
        <Grid size={{ xs: 12, md: 5 }} component={motion.div} variants={fadeUp}>
          <Card sx={{ p: 3 }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Chat-Statistiken
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={donutData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {donutData.map((_, idx) => (
                      <Cell key={idx} fill={DONUT_COLORS[idx % DONUT_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            </Box>
            <Box sx={{ textAlign: 'center', mb: 2 }}>
              <Typography variant="h4" fontWeight={700} sx={{ color: '#00B8D9' }}>
                <AnimatedValue value={chat_stats.total_messages} />
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                Nachrichten gesamt
              </Typography>
            </Box>
            {chat_stats.most_active_lesson && (
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  Aktivste Lektion: <strong>{chat_stats.most_active_lesson.title}</strong>
                  {' '}({chat_stats.most_active_lesson.message_count} Nachrichten)
                </Typography>
              </Box>
            )}
          </Card>
        </Grid>
      </Grid>

      {/* Zone 4 — XP Distribution + Achievement Highlights */}
      <Grid container spacing={3}>
        {/* XP Distribution */}
        <Grid size={{ xs: 12, md: 7 }} component={motion.div} variants={fadeUp}>
          <Card sx={{ p: 3 }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              XP-Verteilung
            </Typography>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={xp_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
                <XAxis dataKey="range" stroke={AXIS_STROKE} fontSize={12} />
                <YAxis stroke={AXIS_STROKE} fontSize={12} allowDecimals={false} />
                <Tooltip
                  contentStyle={TOOLTIP_STYLE}
                  formatter={(value: number) => [`${value} Nutzer`, 'Anzahl']}
                />
                <Bar dataKey="count" name="Nutzer" fill="#8E33FF" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        {/* Achievement Highlights */}
        <Grid size={{ xs: 12, md: 5 }} component={motion.div} variants={fadeUp}>
          <Card sx={{ p: 3 }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Achievement-Highlights
            </Typography>
            <Grid container spacing={2}>
              {achievements_summary.most_common && (
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Card
                    variant="outlined"
                    sx={{
                      p: 2,
                      textAlign: 'center',
                      borderColor: 'rgba(0, 167, 111, 0.3)',
                      bgcolor: 'rgba(0, 167, 111, 0.04)',
                    }}
                  >
                    <Typography variant="h4" sx={{ mb: 0.5 }}>
                      {achievements_summary.most_common.icon}
                    </Typography>
                    <Typography variant="caption" fontWeight={700} sx={{ display: 'block' }}>
                      Haeufigste
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
                      {achievements_summary.most_common.name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#00A76F' }}>
                      {achievements_summary.most_common.unlock_count}x freigeschaltet
                    </Typography>
                  </Card>
                </Grid>
              )}
              {achievements_summary.rarest && (
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Card
                    variant="outlined"
                    sx={{
                      p: 2,
                      textAlign: 'center',
                      borderColor: 'rgba(142, 51, 255, 0.3)',
                      bgcolor: 'rgba(142, 51, 255, 0.04)',
                    }}
                  >
                    <Typography variant="h4" sx={{ mb: 0.5 }}>
                      {achievements_summary.rarest.icon}
                    </Typography>
                    <Typography variant="caption" fontWeight={700} sx={{ display: 'block' }}>
                      Seltenste
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
                      {achievements_summary.rarest.name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#8E33FF' }}>
                      {achievements_summary.rarest.unlock_count}x freigeschaltet
                    </Typography>
                  </Card>
                </Grid>
              )}
              {!achievements_summary.most_common && !achievements_summary.rarest && (
                <Grid size={{ xs: 12 }}>
                  <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center', py: 3 }}>
                    Keine Achievements vorhanden
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Card>
        </Grid>
      </Grid>
    </motion.div>
  );
}
