import { useNavigate } from "react-router-dom";
import NextImg from "/images/next.svg";
import ProfileImg from "/images/profile.svg";
import { useSelector } from "react-redux";

function StartPage() {

  const navigate = useNavigate();
  const isAuthenticated = useSelector(state => state.profile.isAuthenticated);

  const handleProfile = () => {
    if (isAuthenticated) {
      navigate("/list");
    } else {
      navigate("/auth");
    }
  }

  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-[1.875rem]">
      <div className="text-center justify-center text-black text-6xl font-semibold">
        Приветствуем в нашем приложении
        <br />
        для изучения UX!
      </div>
      <div className="w-[59.75rem] text-center justify-center text-black/80 text-3xl">
        Далее Вам будет предложено пройти 2 задания по выбору подходящего места
        для кнопки в интерфейсе, а также мы проверим вашу реакцию на различные
        рекламные баннеры
      </div>
      <div className="flex items-center justify-center gap-4">
        <img
          onClick={handleProfile}
          src={ProfileImg}
          className="w-22 h-22 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
        />
        <img
          src={NextImg}
          onClick={() => navigate("/enterName")}
          className="w-24 h-24 hover:cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out"
        />
      </div>
    </div>
  );
}

export default StartPage;
