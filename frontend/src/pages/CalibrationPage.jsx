import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import NextImg from "/images/next.svg";
import CatImg from "/images/cat-dance.gif";

function CalibrationPage() {
  const navigate = useNavigate();
  const [calibrationStep, setCalibrationStep] = useState(0);
  const [isCooldown, setIsCooldown] = useState(false);
  const totalSteps = 5;

  useEffect(() => {
    if (calibrationStep > 0 && calibrationStep < totalSteps) {
      const handleKeyDown = (event) => {
        if (isCooldown) return;
        if (event.key === "ArrowRight" || event.key === " ") {
          setCalibrationStep(calibrationStep + 1);
          setIsCooldown(true);
          setTimeout(() => setIsCooldown(false), 1500);
        } else if (event.key === "ArrowLeft") {
          setCalibrationStep(calibrationStep - 1);
          setIsCooldown(true);
          setTimeout(() => setIsCooldown(false), 1500);
        }
      };
      window.addEventListener("keydown", handleKeyDown);
      return () => window.removeEventListener("keydown", handleKeyDown);
    }
  }, [calibrationStep, isCooldown, totalSteps]);

  const getDotPosition = () => {
    switch (calibrationStep) {
      case 1:
        return "translate(0, 0)";
      case 2:
        return "translate(calc(100vw - 100%), 0)";
      case 3:
        return "translate(0, calc(100vh - 100%))";
      case 4:
        return "translate(calc(100vw - 100%), calc(100vh - 100%))";
      default:
        return "translate(0, 0)";
    }
  };

  return (
    <>
      {calibrationStep === 0 ? (
        <div className="w-full h-full flex flex-col items-center justify-center gap-[1.875rem]">
          <div className="text-center justify-center text-black text-6xl font-semibold">
            Приступим к калибровке айтрекера
          </div>
          <div className="w-[59.75rem] text-center justify-center text-black/80 text-3xl">
            Сейчас в разных частях экрана будет появляться красная точка.
            Смотрите на нее до тех пор, пока она не пропадет
          </div>
          <div className="flex gap-4">
            <img
              src={NextImg}
              alt="previous"
              onClick={() => navigate("/enterName")}
              className="w-24 h-24 rotate-180 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
            />
            <img
              src={NextImg}
              alt="next"
              onClick={() => setCalibrationStep(1)}
              className="w-24 h-24 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
            />
          </div>
        </div>
      ) : calibrationStep < totalSteps ? (
        <div
          onClick={() => setCalibrationStep(calibrationStep + 1)}
          className="w-full h-full relative"
        >
          <img
            src={CatImg}
            alt="cat"
            className="transition-transform absolute duration-1000 ease-in-out z-0"
            style={{ transform: getDotPosition() }}
          />
          <div
            className="w-6 h-6 bg-red-500 rounded-full absolute animate-pulse transition-transform duration-1000 ease-in-out z-10"
            style={{ transform: getDotPosition() }}
          />
        </div>
      ) : (
        <div className="w-full h-full flex flex-col items-center justify-center gap-[1.875rem]">
          <div className="text-center justify-center text-black text-6xl font-semibold">
            Калибровка завершена!
          </div>
          <div className="w-[59.75rem] text-center justify-center text-black/80 text-3xl">
            Теперь приступим к выполнению заданий
          </div>
          <div className="flex gap-4">
            <img
              src={NextImg}
              alt="previous"
              onClick={() => setCalibrationStep(0)}
              className="w-24 h-24 rotate-180 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
            />
            <img
              src={NextImg}
              alt="next"
              onClick={() => navigate("/tasks/true")}
              className="w-24 h-24 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
            />
          </div>
        </div>
      )}
    </>
  );
}

export default CalibrationPage;
