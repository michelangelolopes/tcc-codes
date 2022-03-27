import React, { useState } from 'react';

import './CovidCaseForm.css';

const CovidCaseForm = (props) => {
  const [enteredRegistrationNumber, setEnteredRegistrationNumber] = useState('');
  const [enteredDate, setEnteredDate] = useState('');

  const registrationNumberChangeHandler = (event) => {
    setEnteredRegistrationNumber(event.target.value);
  };

  const dateChangeHandler = (event) => {
    setEnteredDate(event.target.value);
  };

  const maskChangeHandler = (event) => {
    props.onChangeFilter(event.target.value);
  };

  const submitHandler = (event) => {
    event.preventDefault();

    const data = {
      id: enteredRegistrationNumber,
      mask: props.selected,
      date: new Date(enteredDate),
    };

    fetch('http://127.0.0.1:5000/mult', {
      method: "POST",
      headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'mode': 'no-cors'
      },
      body: JSON.stringify(data)}).then(response => {
        if (response.status >= 200 && response.status < 300) {
            console.log(response.status);}
  });

    // props.onSaveExpenseData(expenseData);
    setEnteredRegistrationNumber('');
    // setEnteredAmount('');
    setEnteredDate('');
    // props.onChangeFilter("no_mask");
  };

  return (
    <form onSubmit={submitHandler}>
      <div className='new-covid-case__controls'>
        <div className='new-covid-case__control'>
          <label>Matrícula</label>
          <input
            type='text'
            value={enteredRegistrationNumber}
            onChange={registrationNumberChangeHandler}
          />
        </div>
        <div className='new-covid-case__control'>
        <label>Máscara utilizada</label>
        <select value={props.selected} onChange={maskChangeHandler}>
          <option value='no_mask'>Sem máscara</option>
          <option value='surgery_mark'>Máscara cirúrgica</option>
          <option value='n95_mask'>Máscara N95</option>
        </select>
      </div>
        <div className='new-covid-case__control'>
          <label>Quando apareceram os sintomas?</label>
          <input
            type='date'
            min='2018-01-01'
            max='2018-12-31'
            value={enteredDate}
            onChange={dateChangeHandler}
          />
        </div>
      </div>
      <div className='new-covid-case__actions'>
        <button type="button" onClick={props.onCancel}>Cancelar registro</button>
        <button type='submit' onClick={props.onSave}>Salvar registro</button>
      </div>
    </form>
  );
};

export default CovidCaseForm;
