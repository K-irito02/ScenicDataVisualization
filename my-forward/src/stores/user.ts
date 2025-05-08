import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, updateProfile as apiUpdateProfile, toggleFavorite as apiToggleFavorite, getFavorites as apiGetFavorites, deleteAccount as apiDeleteAccount, forgotPassword as apiForgotPassword, resetPassword as apiResetPassword, sendEmailCode as apiSendEmailCode, verifyEmailCode as apiVerifyEmailCode } from '../api'

interface UserState {
  token: string
  tokenExpiry: number // 添加token过期时间
  userId: string
  username: string
  email: string
  avatar: string
  location: string
  isAdmin: boolean
  favorites: string[]
}

// 获取存储数据的辅助函数
const getStorageItem = (key: string) => {
  try {
    return sessionStorage.getItem(key) || '';
  } catch (e) {
    console.error(`无法读取${key}:`, e);
    return '';
  }
};

// 设置存储数据的辅助函数
const setStorageItem = (key: string, value: string) => {
  try {
    sessionStorage.setItem(key, value);
  } catch (e) {
    console.error(`无法保存${key}:`, e);
  }
};

// 检查token是否过期
const isTokenExpired = (expiry: number) => {
  if (!expiry) return true;
  return Date.now() > expiry;
};

export const useUserStore = defineStore('user', {
  state: (): UserState => {
    const token = getStorageItem('token');
    const tokenExpiry = parseInt(getStorageItem('tokenExpiry') || '0');
    
    // 如果token已过期，清除token
    if (token && isTokenExpired(tokenExpiry)) {
      console.warn('用户token已过期，将清除登录状态');
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('tokenExpiry');
      return {
        token: '',
        tokenExpiry: 0,
        userId: '',
        username: '',
        email: '',
        avatar: '',
        location: '',
        isAdmin: false,
        favorites: []
      };
    }
    
    console.log('初始化用户store状态，获取到token:', token ? `${token.substring(0, 10)}...` : 'null');
    
    return {
      token,
      tokenExpiry,
      userId: getStorageItem('userId'),
      username: getStorageItem('username'),
      email: getStorageItem('email'),
      avatar: getStorageItem('avatar'),
      location: getStorageItem('location'),
      isAdmin: getStorageItem('isAdmin') === 'true',
      favorites: JSON.parse(getStorageItem('favorites') || '[]')
    }
  },
  
  actions: {
    login(username_or_email: string, password: string) {
      console.log('用户store: 开始登录流程', { username_or_email });
      
      return new Promise((resolve, reject) => {
        apiLogin(username_or_email, password)
          .then(response => {
            console.log('用户store: 登录API返回成功', { status: response.status });
            
            const { token, user_id, username: name, email, avatar, location, is_admin } = response.data;
            console.log('用户store: 解析用户数据', { 
              token: token ? `${token.substring(0, 10)}...` : 'null',
              user_id, 
              name
            });
            
            // 设置token过期时间 (当前时间 + 24小时)
            const tokenExpiry = Date.now() + (24 * 60 * 60 * 1000);
            
            this.setUserInfo({
              token,
              tokenExpiry,
              userId: user_id,
              username: name,
              email,
              avatar,
              location,
              isAdmin: is_admin
            });
            
            resolve(response);
          })
          .catch(error => {
            console.error('用户store: 登录API返回错误', error);
            
            // 确保错误信息正确传递给调用者
            reject(error);
          });
      });
    },
    
    register(username: string, email: string, password: string, code: string) {
      return new Promise((resolve, reject) => {
        apiRegister(username, email, password, code)
          .then(response => {
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    logout(options: { redirectToLogin?: boolean, reason?: string } = { redirectToLogin: true, reason: '' }) {
      console.log('用户store: 开始注销用户');
      
      // 解析当前URL，检查是否已在登录页面
      const isAlreadyOnLoginPage = window.location.pathname.includes('/login') || 
                                   window.location.pathname === '/admin' || 
                                   window.location.pathname === '/register';
      
      // 清除store中的信息
      this.token = '';
      this.tokenExpiry = 0;
      this.userId = '';
      this.username = '';
      this.email = '';
      this.avatar = '';
      this.location = '';
      this.isAdmin = false;
      this.favorites = [];
      
      // 清除sessionStorage中的信息
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('tokenExpiry');
      sessionStorage.removeItem('userId');
      sessionStorage.removeItem('username');
      sessionStorage.removeItem('email');
      sessionStorage.removeItem('avatar');
      sessionStorage.removeItem('location');
      sessionStorage.removeItem('isAdmin');
      sessionStorage.removeItem('favorites');
      
      console.log('用户store: 已清除用户信息');
      
      // 避免重复重定向到登录页
      if (options.redirectToLogin && !isAlreadyOnLoginPage) {
        const redirectUrl = options.reason 
          ? `/login?${options.reason}=true` 
          : '/login';
          
        console.log(`用户store: 准备重定向到 ${redirectUrl}`);
        setTimeout(() => {
          window.location.href = redirectUrl;
        }, 100);
      }
    },
    
    updateProfile(profileData: Partial<UserState>) {
      return new Promise((resolve, reject) => {
        apiUpdateProfile(profileData)
          .then(response => {
            const userData = response.data.user
            this.setUserInfo({
              userId: userData.id,
              username: userData.username,
              email: userData.email,
              avatar: userData.avatar,
              location: userData.location,
              isAdmin: userData.isAdmin
            })
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    sendEmailCode(email: string, isProfileUpdate: boolean = false) {
      return new Promise((resolve, reject) => {
        apiSendEmailCode(email, isProfileUpdate)
          .then(response => {
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    verifyEmailCode(email: string, code: string) {
      return new Promise((resolve, reject) => {
        apiVerifyEmailCode(email, code)
          .then(response => {
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    toggleFavorite(scenicId: string) {
      const index = this.favorites.indexOf(scenicId)
      
      return new Promise((resolve, reject) => {
        apiToggleFavorite(scenicId)
          .then(response => {
            if (response.data.is_favorite) {
              // 添加收藏
              if (index === -1) {
                this.favorites.push(scenicId)
              }
            } else {
              // 取消收藏
              if (index > -1) {
                this.favorites.splice(index, 1)
              }
            }
            
            setStorageItem('favorites', JSON.stringify(this.favorites))
            // 直接返回响应对象
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    fetchFavorites() {
      return new Promise((resolve, reject) => {
        apiGetFavorites()
          .then(response => {
            console.log('获取收藏列表响应:', response.data);
            // 安全地处理收藏ID列表
            let favoriteIds = [];
            if (Array.isArray(response.data)) {
              favoriteIds = response.data.map((item: any) => item.id || item.scenic_id);
            } else if (response.data && Array.isArray(response.data.results)) {
              favoriteIds = response.data.results.map((item: any) => item.id || item.scenic_id);
            }
            this.favorites = favoriteIds;
            setStorageItem('favorites', JSON.stringify(favoriteIds));
            resolve(response);
          })
          .catch(error => {
            console.error('获取收藏列表失败:', error);
            reject(error);
          });
      })
    },
    
    setUserInfo(user: Partial<UserState>) {
      console.log('用户store: 设置用户信息', {
        hasToken: !!user.token,
        userId: user.userId,
        username: user.username,
        tokenExpiry: user.tokenExpiry ? new Date(user.tokenExpiry).toLocaleString() : undefined
      });
      
      if (user.token) {
        this.token = user.token;
        setStorageItem('token', user.token);
        console.log('用户store: 已保存token到sessionStorage');
      }
      
      if (user.tokenExpiry) {
        this.tokenExpiry = user.tokenExpiry;
        setStorageItem('tokenExpiry', user.tokenExpiry.toString());
      }
      
      if (user.userId) {
        this.userId = user.userId;
        setStorageItem('userId', user.userId);
      }
      
      if (user.username) {
        this.username = user.username;
        setStorageItem('username', user.username);
      }
      
      if (user.email) {
        this.email = user.email;
        setStorageItem('email', user.email);
      }
      
      if (user.avatar) {
        this.avatar = user.avatar;
        setStorageItem('avatar', user.avatar);
      }
      
      if (user.location) {
        this.location = user.location;
        setStorageItem('location', user.location);
      }
      
      if (user.isAdmin !== undefined) {
        this.isAdmin = user.isAdmin;
        setStorageItem('isAdmin', user.isAdmin.toString());
      }
      
      if (user.favorites) {
        this.favorites = user.favorites;
        setStorageItem('favorites', JSON.stringify(user.favorites));
      }
    },
    
    // 添加检查token是否有效的方法
    isAuthenticated() {
      return !!this.token && !isTokenExpired(this.tokenExpiry);
    },
    
    getUserInfo(): UserState {
      return {
        token: this.token,
        tokenExpiry: this.tokenExpiry,
        userId: this.userId,
        username: this.username,
        email: this.email,
        avatar: this.avatar,
        location: this.location,
        isAdmin: this.isAdmin,
        favorites: this.favorites
      }
    },
    
    deleteAccount(password: string) {
      return new Promise((resolve, reject) => {
        apiDeleteAccount(password)
          .then(response => {
            // 删除成功后，清除用户信息并登出
            this.logout();
            resolve(response);
          })
          .catch(error => {
            reject(error);
          });
      });
    },
    
    forgotPassword(email: string) {
      return new Promise((resolve, reject) => {
        apiForgotPassword(email)
          .then(response => {
            resolve(response);
          })
          .catch(error => {
            reject(error);
          });
      });
    },
    
    resetPassword(email: string, code: string, password: string) {
      return new Promise((resolve, reject) => {
        apiResetPassword(email, code, password)
          .then(response => {
            resolve(response);
          })
          .catch(error => {
            reject(error);
          });
      });
    }
  }
}) 