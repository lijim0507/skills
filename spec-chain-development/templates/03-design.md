> 角色：详细设计师 ｜ 依据：02-architecture.md ｜ 版本：v1.0 ｜ 状态：待确认

# 1 修订记录/Revision record

1．	版本命名规则，vX.Y，如初版发布为v1.0
Version naming rules, vX.Y. For example, the first version released is v1.0.

2．	文档内容变更，Date应为变更日期；版本号X维持不变，Y增加1，如v1.1；
If the content of the document has changed, Date shall be the date of the change; and the version number X shall remain unchanged and Y shall increase by 1, such as v1.1.

3．	文档内容通过批准，Date为 批准日期；版本号X增加1，Y降为0，如v2.0；
If the document update is approved, Date shall be the approval date; version number X shall be increased by 1, and Y shall be decreased to 0, e.g. v2.0.

| 版本 | 状态 | 变更内容 | 变更日期 | 更改人 | 批准人 |
| --- | --- | --- | --- | --- | --- |
| r1 | 草稿 | 建档 | <YYYY-MM-DD> | <名字> | <名字> |

# 2 简介/INTRODUCTION

<这里简要地介绍要描述的对象，包括文件的目的、背景和文件所服务的读者。>
<This process briefly introduces the object to be described, including the purpose of document the background and the readers served by the document.>

## 2.1 目的/Purpose

<详细描述本文件的目的。>
<Describe the purpose of this document in detail.>

本文档描述了软件详细设计，主要目的是为了描述：软件描述、外部接口、软件分解、动态行为、资源消耗目标。

This document describes the software detail design with the main purpose of describing: software description, external interfaces, software decomposition, dynamic behavior, and resource consumption goals.

## 2.2 范围/Scope

<详细描述本文件的范围。>
<Detailed describe the scope of this document.>

e.g.,

This document only applies to software detailed design process of #Project.

本文档仅适用于[项目]中的软件详细设计流程。

## 2.3 术语、定义和缩略语/ Terms, definitions and Abbreviations

<列出文件中出现的所有缩略语。>
<List all abbreviations that appear in the document.>

| 缩略语 Abbreviation | 解释 Explanation |
| --- | --- |
| PM | Project Manager |
|  |  |
|  |  |
|  |  |
|  |  |

## 2.4 参考/References

<列出所有参考文件及其位置。>
<List all reference documents and their locations.>

| No. | 工作产品名 Work Product Name | 位置 Location |
| --- | --- | --- |
| 1 | Project Plan | …\man.3 |
| 2 | Software Detailed Design Plan | …\swe.3 |
|  |  |  |
|  |  |  |
|  |  |  |

# 3 资源/RESOURCE

## 3.1 角色/Roles

<列出参与这一过程的相关角色和相关信息。>
<List the relevant roles involved in this process and the relevant information.>

| 角色 Role | 姓名 Name | 联系电话 Contact Number | 电子邮件 Email | 备注 Remark |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

## 3.2 相关接口/Relevant Interfaces

参见“软件资源管理表”中SWE.3章节内容

# 4 沟通计划/COMMUNICATION PLAN

参见“软件沟通管理计划”中SWE.2章节内容

# 5 软件组件描述/SOFTWARE COMPONENT DESCRIPTION

<组件的详细描述，包括组件的功能、目标的实现、在软件中的作用和其他信息>。

<Detailed description of the component, including the function of the component, the realization of the goal, the role in the software and other information.>

<此章节内容为继承Swe.2架构设计的内容。>

<This chapter inherits the content of SWE.2 architecture design.>

## 5.1 功能描述/ Function Description

<组件的详细描述，包括组件的功能、目标的实现、在软件中的作用和其他信息>。
<Detailed description of the component, including the function, the realization of the goal, the role in the software and other information.>

## 5.2 组件交互/Component Interaction

<本章用于描述待开发软件组件与其他组件的关系（直接交互）。>

< This chapter is used to describe the relationship (direct interaction) of the software component to be developed with other components. >

<组件交互图>

# 6 接口/Interface

<本章描述组件间接口，以及所有单元之间的接口。>
< This chapter describes the interfaces between components, as well as the interfaces between all units. >

## 6.1 数据结构/Data Structure

<本章介绍了数据结构的设计，包括枚举、结构和其他自定义数据类型。>
<This chapter describes the design of data structures, including enumerations, structures, and other custom data types.>

### 6.1.1 数据结构A/Data Structure A

<下面详细介绍数据结构A的设计。>
<The design of data structure A is described in detail below.>

| 定义 Define |  |
| --- | --- |
| 解释 Explanation |  |

## 6.2 变量/Variable

<本章描述全局变量。 请注意，如果全局变量是自定义类型，则必须在数据结构一章中描述该类型。>
<This chapter describes global variable. Note that if a global variable is of a custom type, that type must be described in the chapter Data Structure.>

### 6.2.1 变量A/Variable A

<下面详细介绍变量A的设计。>
<The design of variable A is described in detail below.>

| 描述 Description |  |
| --- | --- |
| 方向 Direction |  |
| 数据类型 Data Type |  |
| 范围 Range |  |
| 默认值 Default Value |  |

## 6.3 参数/ Parameter

<本章介绍所有重要参数。>
<This chapter describes all important parameters.>

| 参数名 Param Name | 描述 Description | 数据类型 Data Type | 值 Value | 单位 Unit | 转化 Conversion |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

## 6.4 外部函数定义/External Function Definition

### 6.4.1 函数A/Function A

<描述外部函数设计。>
<The design of the external function is described.>

| 原型 Prototype |  |
| --- | --- |
| 描述 Description |  |
| 参数 Parameter |  |
| 返回值 Return Value |  |

# 7 软件组件设计/SOFTWARE COMPONENT DESIGN

## 7.1 组件分解/Component Decomposition

<本章用于描述软件组件的分解结构。它可以包括：单元的结构部署和单元之间的关系。>

<This chapter is used to describe the decomposition structure of software component. It could include the unit structure deployment and relationship between software units. >

## 7.2 静态特性/Static Aspects

### 7.2.1 框架图/Block Diagram

<本章介绍每个子组件的静态交互。> 
<This chapter explains the static interaction of each subcomponent. >

下图示例仅供参考。
The following figure shows an example for reference only.

### 7.2.2 函数列表

| 序号 | 函数名 | 描述 | 定义组件 | 调用组件 | 调用组件 | 调用组件 |
| --- | --- | --- | --- | --- | --- | --- |
| 序号 | 函数名 | 描述 | 定义组件 | 组件1 | 组件2 | …… |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

### 7.2.3 函数关系

通过函数的调用树来表示函数关系。例如:

### 7.2.4 源代码文件清单

| 文件名称 | 描述 | 相对路径 |
| --- | --- | --- |
| 文件名称 | 描述 | 相对路径 |
|  |  |  |
|  |  |  |
|  |  |  |

## 7.3 动态特性/Dynamic Aspects

<本章定义详细设计中与软件架构相关的动态方面，包括相关软件单元之间的交互，以实现组件的动态行为。。下图仅作为参考示例。>
<This chapter explains the dynamic aspects of the detailed design with respect to the software architecture, including the interactions between relevant software units to fulfill the component’s dynamic behavior. The following figure shows an example for reference only.>

### 7.3.1 任务

| 优先级 | 名称 | 类型Type | 堆栈大小 | 描述 | 备注 |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

### 7.3.2 中断

### 7.3.3 定时器

### 7.3.4 事件

### 7.3.5 调度

### 7.3.6 时序图/Sequence Diagram

<下图仅供参考。 通过时序图显示组件内的关键时序过程。>
<The following figure is for reference only. Show the key timing process within the component through timing diagram.>

| 时序图ID |  |
| --- | --- |
| 软件组件 |  |
| 时序图描述 |  |
| 时序图 | 时序图 |

### 7.3.7 活动图/Activity Diagram

<下图仅供参考。 通过活动图显示组件中的关键活动过程。>
<The following figure is for reference only. Show the key activity process in the component through the activity diagram.>

| 活动图ID |  |
| --- | --- |
| 软件组件 |  |
| 活动图描述 |  |
| 活动图 | 活动图 |

### 7.3.8 状态图

| 状态图ID |  |
| --- | --- |
| 软件组件 |  |
| 状态图描述 |  |
| 状态图 | 状态图 |

### 7.3.9 数据流图

| 数据流图ID |  |
| --- | --- |
| 软件组件 |  |
| 数据流图描述 |  |
| 数据流图 | 数据流图 |

# 8 软件单元设计/SOFTWARE UNIT DESIGN

## 8.1 代码生成配置/Configuration for Code Generation

<本章介绍MATLAB自动生成代码的相关配置。> This chapter describes the configuration of MATLAB automatic code generation
<也可以独立的一个文档。但是也需要在SUP.8中进行配置管理。> It can also be a separate document. However, configuration management is also required in SUP.8

## 8.2 软件单元A/Software Unit A

### 8.2.1 说明/Description

<本章详细介绍各个子组件的设计，包括功能实现等信息。>
<This chapter describes the design of each sub-component in detail, including the realization of functions and other information.>

### 8.2.2 函数设计/Function Design

#### 8.2.2.1 函数A/Function A

| 函数ID |  |  |  |  |
| --- | --- | --- | --- | --- |
| 函数名 |  |  |  |  |
| 函数描述 |  |  |  |  |
| 输入/输出 | I/O | 参数 | 类型 | 描述 |
| 参数 |  |  |  |  |
| 返回值 |  |  |  |  |
| 全局变量 |  |  |  |  |
| 静态变量 |  |  |  |  |
| 程 序 流 程 图 |  |  |  |  |

# 9 可追溯性

| 软件架构 | 软件架构 | 软件架构 | 软件详设 | 软件详设 |
| --- | --- | --- | --- | --- |
| ID | ID | ASIL | ID | ASIL |
| 5.2 外部接口/External Interface | 5.2 外部接口/External Interface |  |  |  |
| 5.3.1 数据定义 | 5.3.1 数据定义 |  |  |  |
| 5.3.2组件间的接口设计 | 接口ID1 |  |  |  |
| 5.3.2组件间的接口设计 | 接口ID2 |  |  |  |
| 5.3.2组件间的接口设计 | 接口ID3 |  |  |  |
| 5.3.2组件间的接口设计 | .......... |  |  |  |
| 5.3.3 组件间的依赖关系 | 5.3.3 组件间的依赖关系 |  |  |  |
| 5.3.4.1.2时序 | 5.3.4.1.2时序 |  |  |  |
| 5.3.4.2.2 时序 | 5.3.4.2.2 时序 |  |  |  |
| 5.3.4.3.2 时序 | 5.3.4.3.2 时序 |  |  |  |
| ......... | ......... |  |  |  |
| 5.4.1 开机 | 5.4.1 开机 |  |  |  |
| 5.4.5 关机 | 5.4.5 关机 |  |  |  |
| 5.4.3 工作状态1 | 5.4.3 工作状态1 |  |  |  |
| 5.5.1 闪存地址分配 | 5.5.1 闪存地址分配 |  |  |  |
| 5.5.2 RAM地址分配 | 5.5.2 RAM地址分配 |  |  |  |
| 5.5.3 ROM地址分配 | 5.5.3 ROM地址分配 |  |  |  |
| 5.5.4 EEPROM地址分配 | 5.5.4 EEPROM地址分配 |  |  |  |
| 5.5.5 时间限制设计 | 5.5.5 时间限制设计 |  |  |  |
| 5.5.6 性能/Performance | 5.5.6 性能/Performance |  |  |  |
| 5.6 软件调度机制 | 5.6 软件调度机制 |  |  |  |
| 5.6.1 任务/Task | 5.6.1 任务/Task |  |  |  |
| 5.6.2 中断/Interrupt | 5.6.2 中断/Interrupt |  |  |  |
| 5.6.3 调度机制/Scheduler mechanism | 5.6.3 调度机制/Scheduler mechanism |  |  |  |
| 5.7 异常清单 | 5.7 异常清单 |  |  |  |
| 6 生产、运行、服务和报废要求（仅ASIL要求） | 6 生产、运行、服务和报废要求（仅ASIL要求） |  |  |  |
| 6.1 对生产的要求 | 6.1 对生产的要求 |  |  |  |
| 6.2 对安装、调试和维护的要求 | 6.2 对安装、调试和维护的要求 |  |  |  |

| 软件需求 | 软件需求 | 软件详设 | 软件详设 |
| --- | --- | --- | --- |
| ID | ASIL | ID | ASIL |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

# 10 附录/APPENDIXES
