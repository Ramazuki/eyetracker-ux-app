import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import StartPage from './pages/StartPage';
import CalibrationPage from './pages/CalibrationPage';
import TasksPage from './pages/TasksPage';
import FinalPage from './pages/FinalPage';
import FirstTask from './pages/FirstTask';
import AuthPage from './pages/AuthPage';
import ListPage from './pages/ListPage';
import TestInfoPage from './pages/TestInfoPage';
import EnterNamePage from './pages/EnterNamePage';
import SecondTask from './pages/SecondTask';
import ResultsPage from './pages/ResultsPage';

function App() {
  return (
    <Router>
      <div className='w-full h-full'>
        <Routes>
          <Route path="/" element={<StartPage />} />
          <Route path="/calibration" element={<CalibrationPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/list" element={<ListPage />} />
          <Route path="/testInfo/:testId" element={<TestInfoPage />} />
          <Route path="/enterName" element={<EnterNamePage />} />
          <Route path="/tasks/:isFirstTask/*" element={<TasksPage />}>
            <Route path="task1" element={<FirstTask />} />
            <Route path="task2" element={<SecondTask />} />
          </Route>
          <Route path="/end" element={<FinalPage />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
