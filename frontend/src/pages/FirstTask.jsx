import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import GoogleImg from "/images/google.svg";
import DateImg from "/images/calendar.svg";
import NextImg from "/images/next.svg";

function FirstTask() {
  const navigate = useNavigate();
  const [isTestStarted, setIsTestStarted] = useState(false);
  const [isTestFinished, setIsTestFinished] = useState(false);
  const [buttonPos, setButtonPos] = useState({ x: 0, y: 0 });
  const [timer, setTimer] = useState(5);
  const containerRef = useRef(null);

  const handleMouseMove = (e) => {
    if (!isTestStarted || isTestFinished) return;
    const rect = containerRef.current.getBoundingClientRect();
    setButtonPos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  const startTest = () => {
    setIsTestStarted(true);
    setIsTestFinished(false);
    setTimer(5);
  };

  useEffect(() => {
    if (isTestStarted) {
      if (timer === 0) {
        setIsTestFinished(true);
        setIsTestStarted(false);
        return;
      }
      const interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isTestStarted, timer]);

  return (
    <div
      className="w-full h-full"
      ref={containerRef}
      onMouseMove={handleMouseMove}
      style={{ position: "relative" }}
    >
      <div className="w-[22rem] h-[8.75rem] ml-8 px-4 py-2 flex flex-col gap-2 justify-center items-center rounded-xl outline-[3px] outline-black top-1/2 left-0 -translate-y-1/2 absolute z-10">
        <div className="w-full text-center text-black/80 text-xl">
          Расположите, где считаете нужным,{" "}
          <span className="font-semibold">кнопку регистрации</span>
        </div>
        {!isTestStarted && !isTestFinished && (
          <div className="px-8 py-2 rounded-2xl outline-[3px] outline-[#7EA8E6] flex justify-center items-center">
            <p className="text-xl font-semibold text-[#7EA8E6]">
              Зарегистрироваться
            </p>
          </div>
        )}
        {!isTestStarted && !isTestFinished && (
          <div
            onClick={startTest}
            className="px-8 py-2 absolute -bottom-16 rounded-2xl outline-[3px] outline-[#7EA8E6] flex justify-center items-center cursor-pointer hover:scale-105 transition-[scale] ease-in-out duration-300"
          >
            <p className="text-xl font-semibold text-[#7EA8E6]">Начать</p>
          </div>
        )}
        {isTestStarted && !isTestFinished && (
          <div className="text-xl font-bold text-[#7EA8E6]">
            {timer} сек
          </div>
        )}
      </div>
      <div className="w-[59.75rem] h-full bg-black/[5%] outline-[3px] outline-black absolute top-0 left-1/2 -translate-x-1/2 z-0 p-12 flex flex-col items-center justify-start gap-[10rem]">
        <div className="w-full text-center justify-center text-black text-4xl font-semibold z-10">
          Форма для регистрации
        </div>
        <div className="w-[18rem] flex flex-col justify-center items-center gap-10 z-10">
          <button
            id="google"
            className="w-full h-[2.875rem] rounded-2xl outline-[3px] outline-black flex justify-start items-center gap-4 px-4
            hover:scale-105 cursor-pointer transition-[scale] ease-in-out duration-300"
          >
            <img src={GoogleImg} className="w-6 aspect-square" />
            <p className="text-base font-semibold">Вход с помощью Google</p>
          </button>

          <div
            id="name"
            className="w-full h-[2.875rem] rounded-2xl outline-[3px] outline-black flex justify-start items-center gap-4 px-4 cursor-text"
          >
            <p className="text-lg font-semibold">Имя</p>
          </div>

          <div
            id="surname"
            className="w-full h-[2.875rem] rounded-2xl outline-[3px] outline-black flex justify-start items-center gap-4 px-4 cursor-text"
          >
            <p className="text-lg font-semibold">Фамилия</p>
          </div>

          <div
            id="date"
            className="w-full h-[2.875rem] rounded-2xl outline-[3px] outline-black flex justify-between items-center gap-4 px-4 cursor-text"
          >
            <p className="text-lg font-semibold">01.01.1975</p>
            <img src={DateImg} className="w-6 aspect-square cursor-pointer" />
          </div>

          <div id="sex" className="w-full h-14 relative">
            <div className="absolute top-0 left-0 text-base font-semibold">
              Пол:
            </div>
            <div className="absolute bottom-0 right-0 flex gap-3 justify-end items-center">
              <input
                type="radio"
                name="sex"
                id="male"
                className="outline-1 outline-black rounded-full"
              />
              <label htmlFor="male" className="text-base font-semibold">
                Мужской
              </label>
              <input
                type="radio"
                name="sex"
                id="female"
                className="outline-1 outline-black rounded-full"
              />
              <label htmlFor="female" className="text-base font-semibold">
                Женский
              </label>
            </div>
          </div>
          {isTestFinished && (
            <img
              src={NextImg}
              onClick={() => navigate("/tasks/false")}
              className="w-24 h-24 absolute bottom-8 right-8 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
            />
          )}
        </div>
      </div>
      {isTestFinished && (
        <div
          className="px-8 py-2 rounded-2xl outline-[3px] outline-[#7EA8E6] flex justify-center items-center"
          style={{
            position: "absolute",
            left: buttonPos.x,
            top: buttonPos.y,
            transform: "translate(-50%, -50%)",
            zIndex: 50,
            pointerEvents: "none",
          }}
        >
          <p className="text-xl font-semibold text-[#7EA8E6]">
            Зарегистрироваться
          </p>
        </div>
      )}
    </div>
  );
}

export default FirstTask;
