nixi gcc # 12
nixi cmake # 
nixi autoconf # 
nixi automake # 1.16.5
nixi libtool # 2.4.7

export LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"

cd ~/
mkdir -p ./repos
cd repos

# 
# protobuf
# 
nix-env -iA protobuf3_5 -f https://github.com/NixOS/nixpkgs/archive/99c08670066b13ab8347c6de087cc915fae99165.tar.gz
# git clone --depth=1 -b 'v3.5.1' https://github.com/google/protobuf.git
# zsh -c '
# cd protobuf
# ./autogen.sh
# '

# 
# TBB
# 
    # Doesnt work for arm64 :(
        # wget https://github.com/PINTO0309/TBBonARMv7/raw/master/libtbb-dev_2018U2_armhf.deb
        # sudo dpkg -i ~/libtbb-dev_2018U2_armhf.deb
        # sudo ldconfig
        # rm libtbb-dev_2018U2_armhf.deb
    # Alternative attempt
        git clone https://github.com/syoyo/tbb-aarch64
        cd tbb-aarch64
        sudo apt install -y build-essential
        ./scripts/bootstrap-aarch64-linux.sh
        # ERROR, skipped


# 
# opencv
# 
# Remove previous version
sudo apt autoremove libopencv3
# Install 
wget https://github.com/mt08xx/files/raw/master/opencv-rpi/libopencv3_3.4.3-20180907.1_armhf.deb
sudo apt install -y ./libopencv3_3.4.3-20180907.1_armhf.deb
sudo ldconfig


sudo apt-get install -y libdrm-amdgpu1 libdrm-amdgpu1-dbgsym libdrm-dev libdrm-exynos1 libdrm-exynos1-dbgsym libdrm-freedreno1 libdrm-freedreno1-dbgsym libdrm-nouveau2 libdrm-nouveau2-dbgsym libdrm-omap1 libdrm-omap1-dbgsym libdrm-radeon1 libdrm-radeon1-dbgsym libdrm-tegra0 libdrm-tegra0-dbgsym libdrm2 libdrm2-dbgsym
sudo apt-get install -y libglu1-mesa libglu1-mesa-dev glusterfs-common libglu1-mesa libglu1-mesa-dev libglui-dev libglui2c2
sudo apt-get install -y libglu1-mesa libglu1-mesa-dev mesa-utils mesa-utils-extra xorg-dev libgtk-3-dev libusb-1.0-0-dev
sudo apt-get install -y libgl1-mesa-dev

sudo apt-get install libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev
sudo apt-get install -y libx11-dev
sudo apt-get install -y libusb-dev
 
# nano ../CMakeLists.txt
# add these two lines near the top:
#     set(OPENGL_gl_LIBRARY /usr/lib/aarch64-linux-gnu/libGL.so)
#     set(OPENGL_glx_LIBRARY /usr/lib/aarch64-linux-gnu/libGLX.so)

cmake .. -DBUILD_EXAMPLES=true -DCMAKE_BUILD_TYPE=Release -DFORCE_LIBUVC=true -DGLFW_USE_WAYLAND=ON 