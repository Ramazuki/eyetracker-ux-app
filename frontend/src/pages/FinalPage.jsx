import { useNavigate } from "react-router-dom";
import AgainImg from "/images/again.svg";
import MapImg from "/images/heatmap.svg";
import { useDispatch } from "react-redux";
import { setData } from "../store/testSlice";
import { useEffect } from "react";

function FinalPage() {

  const navigate = useNavigate();
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(setData("test"));
  }, []);

  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-[1.875rem]">
      <div className="text-center justify-center text-black text-6xl font-semibold">
        Спасибо за участие!
      </div>
      <div className="w-[59.75rem] text-center justify-center text-black/80 text-3xl">
        На этом задания подошли к концу. Вы можете пройти тестирование еще раз
        или посмотреть визуализацию своих результатов.
      </div>
      <div className="flex items-center justify-center gap-4">
        <img
          onClick={() => navigate("/")}
          src={AgainImg}
          className="w-[7.625rem] h-[7.625rem] rotate-180 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
        />
        <img
          onClick={() => navigate("/results")}
          src={MapImg}
          className="w-[5.375rem] h-[5.375rem] hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
        />
      </div>
    </div>
  );
}

export default FinalPage;
