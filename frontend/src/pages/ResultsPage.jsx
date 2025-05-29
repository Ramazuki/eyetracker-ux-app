import MapImg from "/images/map.jpg";
import SaccadeImg from "/images/saccade.jpg";
import { useSelector } from "react-redux";
import PreviousImg from "/images/next.svg";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

function ResultsPage() {

  const testList = useSelector((state) => state.testList.testList);
  const currentTestId = useSelector((state) => state.testList.currentTestId);
  const navigate = useNavigate();
  const [isSecondTask, setIsSecondTask] = useState(false);

  const handlePrevious = () => {
    if (isSecondTask) {
      setIsSecondTask(false);
    } else {
      navigate("/end");
    }
  };

  if (!currentTestId || testList[currentTestId - 1].data.length === 0) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center">
        <h1 className="text-black text-5xl">Нет данных</h1>
      </div>
    );
  }

  return (
    <div className="w-full h-full pb-8 flex flex-col items-center justify-end gap-4">
      <img src={isSecondTask ? SaccadeImg : MapImg} alt="results" />
      <div className="flex gap-4">
        <img
          src={PreviousImg}
          alt="previous"
          onClick={handlePrevious}
          className="w-24 h-24 rotate-180 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
        />
        <img
          src={PreviousImg}
          alt="next"
          onClick={() => setIsSecondTask(true)}
          className={`w-24 h-24 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out ${
            isSecondTask ? "hidden" : "flex"
          }`}
        />
      </div>
    </div>
  );
}

export default ResultsPage;
