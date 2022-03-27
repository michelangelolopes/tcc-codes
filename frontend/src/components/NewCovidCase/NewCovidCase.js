import React, { useState } from 'react';

import CovidCaseForm from './CovidCaseForm';
import './NewCovidCase.css';

const NewCovidCase = (props) => {
  const [isEditing, setIsEditing] = useState(false);

  // const saveExpenseDataHandler = (enteredExpenseData) => {
  //   const expenseData = {
  //     ...enteredExpenseData,
  //     id: Math.random().toString(),
  //   };
  //   props.onAddExpense(expenseData);
  //   setIsEditing(false);
  // };

  const startEditingHandler = () => {
    setIsEditing(true);
  };

  const stopEditingHandler = () => {
    setIsEditing(false);
    filterChangeHandler("no_mask");
  };
  
  const [choosedMask, setChoosedMask] = useState('no_mask');

  const filterChangeHandler = (mask) => {
    setChoosedMask(mask);
  };

  return (
    <div className='new-covid-case'>
      {!isEditing && (
        <button onClick={startEditingHandler}>Registrar caso de contaminação</button>
      )}
      {isEditing && (
        <CovidCaseForm
          onSave={stopEditingHandler}
          onCancel={stopEditingHandler}
          selected={choosedMask}
          onChangeFilter={filterChangeHandler}
        />
      )}
    </div>
  );
};

export default NewCovidCase;
