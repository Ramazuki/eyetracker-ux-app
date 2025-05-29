import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Img1 from "/images/ad1.png";
import Img2 from "/images/ad2.jpg";
import Img3 from "/images/ad3.jpg";

function SecondTask() {
  const navigate = useNavigate();
  const images = [Img1, Img2, Img3];
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    if (current < images.length - 1) {
      const timer = setTimeout(() => setCurrent(current + 1), 5000);
      return () => clearTimeout(timer);
    } else {
      const timer = setTimeout(() => navigate("/end"), 5000);
      return () => clearTimeout(timer);
    }
  }, [current, images.length, navigate]);

  return (
    <div className="w-full h-full">
      <div className="w-[59.75rem] h-full bg-black/[5%] outline-[3px] outline-black absolute top-0 left-1/2 -translate-x-1/2 z-0 flex flex-col items-center justify-center gap-[1.875rem]">
        <img
          src={images[current]}
          alt={`task-img-${current + 1}`}
          className="w-full"
        />
      </div>
    </div>
  );
}

export default SecondTask;
