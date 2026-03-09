import { Typography } from '@mui/material';
import { useParams } from 'react-router-dom';

export default function LessonPage() {
  const { id } = useParams();
  return <Typography variant="h4">Lektion {id}</Typography>;
}
