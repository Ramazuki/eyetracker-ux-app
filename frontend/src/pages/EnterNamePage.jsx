import { useNavigate } from "react-router-dom";
import NextImg from "/images/next.svg";
import { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { addTest, setCurrentTestId, setName } from "../store/testSlice";

function EnterNamePage() {

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [nameTmp, setNameTmp] = useState("");
  const currentTestId = useSelector((state) => state.testList.currentTestId);
  const testList = useSelector((state) => state.testList.testList);

  const next = () => {
    if (currentTestId) {
      dispatch(setName(nameTmp));
    } else {
      dispatch(addTest({
        id: testList.length + 1,
        name: nameTmp,
        data: [],
      }));
      dispatch(setCurrentTestId(testList.length + 1));
    }
    navigate("/calibration");
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-[1.875rem]">
      <div className="text-center justify-center text-black text-6xl font-semibold">
        Но для начала нам нужно
        <br />
        узнать Вас поближе
        <br />и откалибровать айтрекер
      </div>
      <div className="w-[59.75rem] text-center justify-center text-black/80 text-3xl">
        Введите свое имя
      </div>
      <input
        type="text"
        value={nameTmp}
        onChange={(e) => setNameTmp(e.target.value)}
        className="w-[19.6875rem] h-[2.875rem] px-3 bg-white border-3 border-black rounded-[10px] text-black text-2xl focus:outline-none"
        required
      />
      <div className="flex gap-4">
        <img
          src={NextImg}
          alt="previous"
          onClick={() => navigate("/")}
          className="w-24 h-24 rotate-180 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
        />
        <img
          src={NextImg}
          alt="next"
          onClick={next}
          className={`w-24 h-24 transition-[scale] duration-300 ease-in-out ${nameTmp.replaceAll(" ", "").length > 0 ? "opacity-100 hover:cursor-pointer hover:scale-110 flex" : "opacity-50 cursor-not-allowed hidden"}`}
        />
      </div>
    </div>
  );
}

export default EnterNamePage;
