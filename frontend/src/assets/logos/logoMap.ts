import defaultLogo from './default.svg';
import node from './node.png';
import python from './python.png';
import java from './java.png';
import go from './go.png';
import git from './git.png';
import vscode from './vscode.png';
import docker from './docker.png';
import web from './webdev.png';
import backend_python from './backend-python.png';
import backend_node from './backend-node.png';
import fullstack from './fullstack.png';
import ai_ml from './AI-ML.png';
import data_science from './data-science.png';
import game_dev from './game-dev.png';
import beautifulSoup4 from './beautifulsoup4.jpg';
import black from './black.png';
import celery from './celery.jpg';
import django from './django.png';
import fastapi from './fastapi.png';
import flask from './flask.png';
import gradio from './gradio.png';
import isortLogo from './isort.jfif';
import jupyterlab from './jupyterlab.png';
import jupyterNotebook from './jupyternotebook.png';
import langchain from './langchain.png';
import llamaIndex from './LlamaIndex.png';
import matplotlib from './matplotlib.png';
import numpy from './numpy.png';
import opencv from './OpenCV.png';
import pandas from './pandas.png';
import pillow from './pillow.png';
import pydantic from './pydantic.png';
import pytest from './pytest.png';
import pythonPoetry from './Python Poetry.png';
import pythonDotenv from './python-dotenv.png';
import pytorch from './pytorch.png';
import redis from './Redis.png';
import requests from './requests.png';
import ruff from './ruff.png';
import scikitLearn from './scikit-learn.png';
import scipy from './scipy.png';
import seaborn from './seaborn.png';
import sqlalchemy from './SQLAlchemy.png';
import streamlit from './Streamlit.png';
import tensorflow from './tensorflow.png';
import transformers from './Transformers.png';
import uvicorn from './uvicorn.png';

// Newly added logo imports
import reactLogo from './react.png';
import nextjs from './nextjs.jpeg';
import express from './express-js.webp';
import nestjs from './nestjs.jfif';
import vue from './vue.jfif';
import angular from './angular.jfif';
import svelte from './Svelte.png';
import tailwindcss from './Tailwind CSS.png';
import axios from './Axios.png';
import socketIo from './Socket.io.png';
import prisma from './prisma.png';
import typescriptLogo from './TypeScript.png';
import redux from './Redux.png';
import reactRouter from './reactrouter.png';
import vite from './Vite.js.png';
import webpack from './Webpack.png';
import babel from './Babel.png';
import eslint from './ESLint.png';
import prettier from './prettier.png';
import jest from './Jest.png';
import vitest from './vitest.webp';
import mocha from './Mocha.png';
import nodemon from './Nodemon.png';
import fastify from './Fastify.png';
import electron from './Electron.png';
import playwright from './Playwrite.png';
import cypress from './Cypress.png';
import springboot from './springboot.png';
import springsecurity from './springsecurity.png';
import springdata from './springdata.png';
import maven from './Maven.png';
import gradle from './Gradle.png';
import junit from './JUnit.png';
import hibernate from './Hibernate.png';
import lombok from './lombok.png';
import log4j from './log4j.png';
import jackson from './jackson.png';
import apachecommons from './apachecommons.png';
import junitjupiter from './junitjupiter.png';
import mockito from './mockito.png';
import gin from './gin.png';
import fiber from './fiber.png';
import echo from './echo.png';
import gorm from './gorm.png';
import cobra from './cobra.png';
import viper from './viper.png';
import chi from './chi.png';
import zap from './zap.png';
import gokit from './gokit.png';
import testify from './testify.png';

const logos: Record<string, string> = {
  default: defaultLogo,
  node,
  python,
  java,
  go,
  git,
  vscode,
  docker,
  web,
  backend_python,
  backend_node,
  fullstack,
  ai_ml,
  data_science,
  game_dev,
  beautifulsoup4: beautifulSoup4,
  black,
  celery,
  django,
  fastapi,
  flask,
  gradio,
  isort: isortLogo,
  jupyterlab,
  notebook: jupyterNotebook,
  langchain,
  'llama-index': llamaIndex,
  matplotlib,
  numpy,
  'opencv-python': opencv,
  pandas,
  pillow,
  pydantic,
  pytest,
  poetry: pythonPoetry,
  'python-dotenv': pythonDotenv,
  torch: pytorch,
  redis,
  requests,
  ruff,
  'scikit-learn': scikitLearn,
  scipy,
  seaborn,
  sqlalchemy,
  streamlit,
  tensorflow,
  transformers,
  uvicorn,

  // New packages mappings
  react: reactLogo,
  next: nextjs,
  express,
  nestjs,
  vue,
  angular,
  svelte,
  tailwindcss,
  axios,
  'socket.io': socketIo,
  prisma,
  typescript: typescriptLogo,
  'redux-toolkit': redux,
  'react-router-dom': reactRouter,
  vite,
  webpack,
  babel,
  eslint,
  prettier,
  jest,
  vitest,
  mocha,
  nodemon,
  fastify,
  electron,
  playwright,
  cypress,
  'spring-boot': springboot,
  'spring-security': springsecurity,
  'spring-data': springdata,
  maven,
  gradle,
  junit,
  hibernate,
  lombok,
  log4j,
  jackson,
  'apache-commons': apachecommons,
  'junit-jupiter': junitjupiter,
  mockito,
  gin,
  fiber,
  echo,
  gorm,
  cobra,
  viper,
  chi,
  zap,
  'go-kit': gokit,
  testify,
};

export function getLogo(id: string) {
  return logos[id] ?? logos.default;
}

export default logos;
