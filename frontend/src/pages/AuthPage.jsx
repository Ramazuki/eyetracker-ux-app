import { useEffect, useState } from "react";
import EyeImg from "/images/eye.svg";
import EyeClosedImg from "/images/crossed-eye.svg";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { setIsAuthenticated } from "../store/profileSlice";

function AuthPage() {
  
  const [showPassword, setShowPassword] = useState(false);
  const login = useSelector(state => state.profile.login);
  const password = useSelector(state => state.profile.password);
  const [loginTmp, setLoginTmp] = useState("");
  const [passwordTmp, setPasswordTmp] = useState("");
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [isAuthFailed, setIsAuthFailed] = useState(false);

  const checkAuth = () => {
    if (loginTmp === login && passwordTmp === password) {
      dispatch(setIsAuthenticated(true));
      navigate("/list");
    } else {
      setIsAuthFailed(true);
    }
  }

  return (
    <div className="w-full h-full flex items-center justify-center">
      <div className="w-[47.8125rem] h-[54.125rem] bg-white rounded-[28px] flex flex-col items-center
      justify-around relative border-3 border-black px-[10.625rem] py-20">
        <h1 className="text-black text-8xl">
          Вход
        </h1>
        <div id="input-container" className="w-full flex flex-col items-center justify-center gap-4">
          <div className="w-full h-[2.875rem] flex justify-between items-center">
            <p className="text-black text-2xl">
              Логин
            </p>
            <input
              required
              type="text"
              value={loginTmp.replaceAll(" ", "")}
              onChange={e => setLoginTmp(e.target.value)}
              className="w-[19.6875rem] h-full px-3 bg-white border-3 border-black rounded-[10px] text-black text-2xl focus:outline-none"
            />
          </div>
          <div className="w-full h-[2.875rem] flex justify-between items-center">
            <p className="text-black text-2xl">
              Пароль
            </p>
            <div className="relative w-[19.6875rem] h-full flex items-center">
              <input
                type={showPassword ? "text" : "password"}
                value={passwordTmp.replaceAll(" ", "")}
                onChange={e => setPasswordTmp(e.target.value)}
                className="w-full h-full px-3 bg-white border-3 border-black rounded-[10px] text-black text-2xl pr-12 focus:outline-none"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer"
                tabIndex={-1}
              >
                {showPassword ? <img src={EyeImg} className="w-8 h-8" /> : <img src={EyeClosedImg} className="w-8 h-8" />}
              </button>
            </div>
          </div>
        </div>
        <div id="buttons-container" className="w-full flex flex-col items-center justify-center gap-4">
          <button
            onClick={checkAuth}
            disabled={!loginTmp || !passwordTmp}
            className={`w-full h-[3.4375rem] bg-white rounded-[18px] text-black text-2xl border-3 border-black transition-[scale] duration-300 ease-in-out ${(!loginTmp || !passwordTmp) ? 'opacity-50 cursor-not-allowed hover:scale-100' : 'cursor-pointer hover:scale-105'}`}
          >
            Войти
          </button>
        </div>
        {isAuthFailed && <p id="pswd-wrong" className={`text-red-500 text-xl absolute bottom-10`}>Неверный логин или пароль</p>}
        <p id="exit" onClick={() => navigate("/")} className="text-black text-3xl absolute top-6 left-12 cursor-pointer hover:scale-110 transition-[scale] duration-300 ease-in-out">
          &lt;-
        </p>
      </div>
    </div>
  );
}

export default AuthPage;